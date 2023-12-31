# django_project/users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import  login, logout, authenticate, get_user_model
import secrets
import string
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from. decorators import user_not_authenticated
from .forms import ConductorRegistrationForm, CashierRegistrationForm
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils import timezone
from django.core.mail import EmailMessage
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from .tokens import account_activation_token
from .models import DataCrawl,CurrentPrice, CashierTransaction
from django.db.models.query_utils import Q
from users.models import CustomUser
from datetime import date, datetime
from .forms import KilometerForm
from math import ceil
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from .models import TransportationRecord
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import TransportationRecord
import googlemaps
import math


# Create your views here.
def activateEmail(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('activation.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
            received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
    else:
        messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')


def conductorScanner(request):
    
    return render(request, 'conductor/conductorScanner.html')


def generate_random_transpo_sn(length=25):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

@csrf_exempt
@login_required  
def scan_qr_code(request):
    if request.method == 'POST':
        scan_type = request.POST.get('scan_type')
        extracted_data = request.POST.get('extracted_data')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        # Get the currently logged-in user's userSN
        user = request.user  # Assuming you have set up user authentication
        userSN = user.userSN

        if scan_type == 'out':
            # Update existing records with the same extracted data and scan type "in"
            updated_records = TransportationRecord.objects.filter(extracted_data=extracted_data, scan_type='in')
            if updated_records.exists():
                updated_records.update(
                    latitudeOUT=latitude,
                    longitudeOUT=longitude,
                    scan_type='out'
                )
            else:
                return JsonResponse({'error': 'Not yet scanned in'})

        elif scan_type == 'in':
            # Generate a unique 25-character TranspoSN
            transpo_sn = generate_random_transpo_sn()

            # Create a new TransportationRecord instance and save it to the database
            record = TransportationRecord(
                scan_type=scan_type,
                extracted_data=extracted_data,
                latitudeIN=latitude,
                longitudeIN=longitude,
                latitudeOUT=None,
                longitudeOUT=None,
                TranspoSN=transpo_sn,
                user=userSN  # Assign the userSN of the currently logged-in user
            )

            record.save()

        return JsonResponse({'message': 'Data saved successfully'})

    return JsonResponse({'message': 'Invalid request method'}, status=400)


@login_required
def ConTransaction(request):
    gmaps = googlemaps.Client(key='AIzaSyCQbrn9uYAhVxweNwKpYb5yBYaVURtC6oM')
    records = TransportationRecord.objects.all()

    for record in records:
        if record.latitudeIN is not None and record.longitudeIN is not None and record.latitudeOUT is not None and record.longitudeOUT is not None:
            origin = (record.latitudeIN, record.longitudeIN)
            destination = (record.latitudeOUT, record.longitudeOUT)

            # Use the Google Maps Distance Matrix API to calculate driving distance
            result = gmaps.distance_matrix(origin, destination, mode="driving")

            # Extract and store the distance in the record
            if 'rows' in result and result['rows'][0]['elements'][0]['status'] == 'OK':
                distance = result['rows'][0]['elements'][0]['distance']['value'] / 1000.0  # Convert meters to kilometers
                record.km = distance
                record.save()

                # Find a CustomUser with the matching userSN
                try:
                    user = CustomUser.objects.get(userSN=record.extracted_data)
                    record.commuterStatus = user.status  # Set the commuterStatus to the user's status
                except CustomUser.DoesNotExist:
                    # Handle the case when no matching user is found (e.g., set a default status)
                    record.commuterStatus = "Unknown"

                try:
                    user = CustomUser.objects.get(userSN=record.user)
                    record.TranspoType = user.TransportationType  # Set the commuterStatus to the user's status
                except CustomUser.DoesNotExist:
                    # Handle the case when no matching user is found (e.g., set a default status)
                    record.commuterStatus = "Unknown"
                record.save()

    if record.km is not None and record.TranspoType == "PUJ":
        try:
            current_price = CurrentPrice.objects.get(Num=1)
            initial_price = CurrentPrice.objects.filter(Num=1).first()
            succeeding_price = CurrentPrice.objects.filter(Num=1).order_by('Num').first()

            initial_distance = 4.10
            succeeding_distance = max(0, record.km - initial_distance)
            rounded_succeeding_distance = math.ceil(succeeding_distance)

            # Set the multiplier based on the commuterStatus
            multiplier = 1.0 if record.commuterStatus == "Ordinary" else 0.80

            record.price = (
                current_price.CurrentFarePUJ * multiplier if record.km < 4.10
                else (initial_price.CurrentFarePUJ + (succeeding_price.CurrentSucceedingPUJ * rounded_succeeding_distance)) * multiplier
            )

            user = CustomUser.objects.get(userSN=record.extracted_data)
            if user.balance is not None and user.balance >= record.price:
                user.balance -= record.price
                user.save()
            else:
                # Handle insufficient balance or other cases
                pass

        except (CurrentPrice.DoesNotExist, CustomUser.DoesNotExist):
            # Handle the case when no matching CurrentPrice or user is found
            record.price = 0  # Set a default price

        record.save()

    elif record.km is not None and record.TranspoType == "Modernized PUJ":
        try:
            current_price = CurrentPrice.objects.get(Num=1)
            initial_price = CurrentPrice.objects.filter(Num=1).first()
            succeeding_price = CurrentPrice.objects.filter(Num=1).order_by('Num').first()

            initial_distance = 4.10
            succeeding_distance = max(0, record.km - initial_distance)
            rounded_succeeding_distance = math.ceil(succeeding_distance)

            # Set the multiplier based on the commuterStatus
            multiplier = 1.20 if record.commuterStatus == "Ordinary" else 0.80

            record.price = (
                current_price.CurrentFarePUJ * multiplier if record.km < 4.10
                else (initial_price.CurrentFarePUJ * multiplier) + (succeeding_price.CurrentSucceedingPUJ * rounded_succeeding_distance)
            )

            record.save()

        except CurrentPrice.DoesNotExist:
            # Handle the case when no matching CurrentPrice is found
            record.price = 0  # Set a default price
        record.save()
# Additional logic for other cases can be added as needed

    elif record.km is not None and record.TranspoType == "AirConditioned PUJ":
        try:
            current_price = CurrentPrice.objects.get(Num=1)
            initial_price = CurrentPrice.objects.filter(Num=1).first()
            succeeding_price = CurrentPrice.objects.filter(Num=1).order_by('Num').first()

            initial_distance = 4.10
            succeeding_distance = max(0, record.km - initial_distance)
            rounded_succeeding_distance = math.ceil(succeeding_distance)

            # Set the multiplier based on the commuterStatus
            multiplier = 1.20 if record.commuterStatus == "Ordinary" else 0.80

            record.price = (
                current_price.CurrentFarePUJ * multiplier if record.km < 4.10
                else (initial_price.CurrentFarePUJ * multiplier) + ((succeeding_price.CurrentSucceedingPUJ * multiplier) * rounded_succeeding_distance)
            )

            record.save()

        except CurrentPrice.DoesNotExist:
            # Handle the case when no matching CurrentPrice is found
            record.price = 0  # Set a default price
        record.save()
    # Additional logic for other cases can be added as needed


    elif record.km is not None and record.TranspoType == "Regular Bus":
        try:
            current_price = CurrentPrice.objects.get(Num=1)
            initial_price = CurrentPrice.objects.filter(Num=1).first()
            succeeding_price = CurrentPrice.objects.filter(Num=1).order_by('Num').first()

            initial_distance = 4.10
            succeeding_distance = max(0, record.km - initial_distance)
            rounded_succeeding_distance = math.ceil(succeeding_distance)

            record.price = (
                current_price.CurrentFareBus if record.km < 5.10
                else initial_price.CurrentFarePUJ + (succeeding_price.CurrentSucceedingBus * rounded_succeeding_distance)
            )

            record.save()

        except CurrentPrice.DoesNotExist:
            # Handle the case when no matching CurrentPrice is found
            record.price = 0  # Set a default price
        record.save()

# Additional logic for other cases can be added as needed


    elif record.km is not None and record.TranspoType == "Modernized Bus":
        try:
            current_price = CurrentPrice.objects.get(Num=1)
            initial_price = CurrentPrice.objects.filter(Num=1).first()
            succeeding_price = CurrentPrice.objects.filter(Num=1).order_by('Num').first()

            initial_distance = 4.10
            succeeding_distance = max(0, record.km - initial_distance)
            rounded_succeeding_distance = math.ceil(succeeding_distance)

            record.price = (
                current_price.CurrentFareBus if record.km < 4.10
                else initial_price.CurrentFarePUJ + ((succeeding_price.CurrentFareBus * 1.20) * rounded_succeeding_distance)
            )

            record.save()

        except CurrentPrice.DoesNotExist:
            # Handle the case when no matching CurrentPrice is found
            record.price = 0  # Set a default price
        record.save()
# Additional logic for other cases can be added as needed

    unprocessed_records = TransportationRecord.objects.filter(processed=False)

    for transportation_record in unprocessed_records:
     if transportation_record.price is not None:

        # Find the matching CustomUser based on userSN
        try:
            user = CustomUser.objects.get(userSN=transportation_record.extracted_data)
        except CustomUser.DoesNotExist:
            # Handle the case where there is no matching user
            # You may want to log this or handle it accordingly
            continue

        # Process the deduction from balance
        user.balance -= transportation_record.price
        user.save()

        # Mark the TransportationRecord as processed
        transportation_record.processed = True
        transportation_record.save()

    return render(request, 'conductor/ConTransaction.html', {'records': records})


def homepage(request):
    return render(request=request, template_name='home.html')

def welcome(request):
    if request.user.is_authenticated:
        if request.user.UserGroup == "user":
            return redirect('commuter')
        elif request.user.UserGroup == "cashier":
            return redirect('cashier')
        elif request.user.UserGroup == "conductor":
            return redirect('conductor')
        elif request.user.is_superuser:
            return redirect('admin')
    
    # If the user is not authenticated or doesn't match any specific group, show the welcome page
    return render(request=request, template_name='welcome.html')

@login_required
def commuter(request):


    return render(request, 'commuter/userHome.html')

@login_required
def UWallet(request):

    fare = CurrentPrice.objects.filter(Num='1')
    user = request.user



    context ={
    'fare' : fare,
    'user': user,
    }

    return render(request, 'commuter/UWallet.html',context)

@login_required
def UTransaction(request):

    records = TransportationRecord.objects.all()
    return render(request, 'commuter/UTransaction.html', {'records': records})

@login_required
def UTransactionCashier(request):

    records = CashierTransaction.objects.all()
    return render(request, 'commuter/UTransactionCashier.html', {'records': records})

@login_required
def cashier(request):
    query = request.GET.get('q')

    if query:
        # Use Q objects to build a complex query for searching
        results = CustomUser.objects.filter(
            Q(userSN__icontains=query) |
            Q(last_name__icontains=query) |
            Q(middle_name__icontains=query) |
            Q(first_name__icontains=query) |
            Q(email__icontains=query) |
            Q(username__icontains=query)
        )
    else:
        # If no query is provided, return all users
        results = CustomUser.objects.filter(UserGroup='user')

    return render(request, 'cashier/cashierHome.html', {'results': results, 'query': query})

@login_required
def cTransaction(request):
    records = CashierTransaction.objects.all()
    return render(request, 'cashier/cashierTransaction.html', {'records': records})

@login_required
def update_balance(request, user_id):
    commuter = get_object_or_404(CustomUser, id=user_id)  # Get the user being updated

    if request.method == 'POST':
        # Update the user's balance here
        new_balance = request.POST.get('balance')
        commuter.balance = new_balance

        # Generate a unique TransactionID
        transaction_id = generate_transaction_id()

        # Get the UserSN of the user being updated
        commuterSN = commuter.userSN  # Assuming UserSN is the field in CustomUser model

        # Get the UserSN of the logged-in cashier
        cashierSN = request.user.userSN  # Assuming UserSN is the field in CustomUser model


        # Create a new CashierTransaction entry
        paid_amount = request.POST.get('amount')
        if paid_amount:

            change = float(new_balance) - float(paid_amount)

            transaction = CashierTransaction(
                TransactionID=transaction_id,
                CashierSN=cashierSN,
                CommuterSN=commuterSN,
                CashIn=new_balance,
                paidAmount=paid_amount,
                change=change,
                DateIn=datetime.now()
            )
            transaction.save()

        commuter.save()  # Save the commuter's updated balance
        messages.success(request, 'Balance updated successfully!')


        return HttpResponseRedirect('/cashier/')  # Redirect to the cashier page

    return render(request, 'cashierHome.html', {'user': commuter})


def generate_transaction_id():
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(25))

@login_required
def CashierScan(request):

    return render(request, 'cashier/scanning.html')

@login_required
def conductor(request):

    return render(request=request, template_name='conductor/conductorHome.html')


@login_required
def admin(request):


    return render(request=request, template_name='admin/adminPage.html')

@login_required
def account_management(request):

    return render(request,'admin/account/accountManagement.html' )

@login_required
def validation(request):
    commuter_users = CustomUser.objects.filter(UserGroup='user')

    return render(request,'admin/account/validate.html', {'commuter_users': commuter_users} )

def update_validation(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Update the validation status to True
    user.verified = True
    user.save()
    
    return redirect('validation')

@login_required
def create_conductor(request):

    placeholders = {
        'contactNumber_placeholder': '09*********',
        'emergencyContact_placeholder': '09*********',
    }

    if request.method == 'POST':
        form = ConductorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)  # Create the user object without saving it
            user.email = form.cleaned_data['email']
            user.is_active=False
            
            # Generate a unique userSN
            userSN = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(20))
            user.userSN = userSN

            # Combine "TransitSynch: " with userSN
            qr_data = f"TransitSynch:{userSN}"
            # Set UserGroup to "Commuter"
            user.UserGroup = "conductor"

            user.DPA = True
            user.verified = True

                # Generate a QR code using userSN and save it to 'QR' field
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            user.QR.save(f'qr_{userSN}.png', ContentFile(buffer.getvalue()), save=False)

            

            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('account_management')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = ConductorRegistrationForm()

    return render(
        request=request,
        template_name="admin/account/create_conductor.html",
        context={"form": form, "placeholders": placeholders}
    )


@login_required
def create_cashier(request):

    placeholders = {
        'contactNumber_placeholder': '09*********',
        'emergencyContact_placeholder': '09*********',
    }

    if request.method == 'POST':
        form = CashierRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)  # Create the user object without saving it
            user.email = form.cleaned_data['email']
            user.is_active=False

            qr_data = f"TransitSynch:{userSN}"
            # Generate a unique userSN
            userSN = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(20))
            user.userSN = userSN

            # Set UserGroup to "Commuter"
            user.UserGroup = "cashier"
            user.DPA = True
            user.verified = True

                # Generate a QR code using userSN and save it to 'QR' field
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            user.QR.save(f'qr_{userSN}.png', ContentFile(buffer.getvalue()), save=False)



            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('account_management')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = CashierRegistrationForm()

    return render(
        request=request,
        template_name="admin/account/create_cashier.html",
        context={"form": form, "placeholders": placeholders}
    )


@login_required
def track_prices(request):
    url = "https://www.globalpetrolprices.com/Philippines/"
    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser")

    tags = doc.find_all("tr")
    parent = tags[2]
    prices = parent.find_all("td")

    # Extract the text content inside each <td> element
    extracted_data = [price.get_text(strip=True) for price in prices]

    # Organize the data into date, PHP price, and USD price
    date = extracted_data[0]
    php_price = extracted_data[1]
    usd_price = extracted_data[2]

    # Query the database to get the latest CurrentPrice object
    latest_price = CurrentPrice.objects.last()

    # Convert the price values to floating-point numbers
    php_price_float = float(php_price)
    current_diesel_float = float(latest_price.CurrentDiesel)

    # Calculate the result
    if current_diesel_float != 0:
        calculation_result = (php_price_float - current_diesel_float) / current_diesel_float
    else:
        # Handle the case where the denominator is zero
        calculation_result = None  # You can customize this behavior

    if calculation_result is not None:
        second_calculation_result = calculation_result * 0.35 + 1
    else:
        second_calculation_result = None

    if second_calculation_result is not None:
        third_calculation_result = second_calculation_result * float(latest_price.CurrentFarePUJ)
        fourth_calculation_result = second_calculation_result * float(latest_price.CurrentSucceedingPUJ)
        fifth_calculation_result = second_calculation_result * float(latest_price.CurrentFareBus)
        sixth_calculation_result = second_calculation_result * float(latest_price.CurrentSucceedingBus)
    else:
        third_calculation_result = None
        fourth_calculation_result = None
        fifth_calculation_result = None
        sixth_calculation_result = None


    # Handle the kilometer input form
    fare = None

    if request.method == 'POST':
        kilometer_form = KilometerForm(request.POST)

        if kilometer_form.is_valid():
            kilometers = kilometer_form.cleaned_data['kilometers']
            selected_car_type = kilometer_form.cleaned_data['car_type']

            # Retrieve the current price information
            current_price = CurrentPrice.objects.first()

            if selected_car_type == 'Modernized Bus':
                # Set the threshold to 5 kilometers for "Modernized Bus"
                threshold_kilometers = 5
            else:
                threshold_kilometers = 4

            # Check if kilometers are less than or equal to 4
            if kilometers <= 4:
                if selected_car_type == 'Modernized PUJ':
                    fare = current_price.CurrentFarePUJ * 1.20 
                elif selected_car_type == 'AirConditioned PUJ':
                    fare = current_price.CurrentFarePUJ * 1.20
                elif selected_car_type == 'Modernized Bus':
                    fare = current_price.CurrentFareBus 
                else:
                    fare = current_price.CurrentFarePUJ
            else:
            # Calculate the fare for kilometers exceeding 4, adding cost for each 1 kilometer
                excess_kilometers = ceil(kilometers - threshold_kilometers)
                if selected_car_type == 'Modernized PUJ':
                    fare = current_price.CurrentFarePUJ * 1.20 + (excess_kilometers * current_price.CurrentSucceedingPUJ)
                elif selected_car_type == 'AirConditioned PUJ':
                    fare = current_price.CurrentFarePUJ * 1.20 + (excess_kilometers * (1.20 * current_price.CurrentSucceedingPUJ))
                elif selected_car_type == 'Modernized Bus':
                    fare = current_price.CurrentFareBus + (excess_kilometers * current_price.CurrentSucceedingBus)
                else:
                    fare = current_price.CurrentFarePUJ + (excess_kilometers * current_price.CurrentSucceedingPUJ)
        else:
            fare = None  # Handle invalid input
    else:
        kilometer_form = KilometerForm()  # Create a new form instance

    context = {
        'date': date,
        'php_price': php_price,
        'usd_price': usd_price,
        'latest_price': latest_price,
        'calculation_result': calculation_result,
        'second_calculation_result': second_calculation_result,
        'third_calculation_result': third_calculation_result,
        'fourth_calculation_result': fourth_calculation_result,
        'fifth_calculation_result': fifth_calculation_result,
        'sixth_calculation_result': sixth_calculation_result,
        'kilometer_form': kilometer_form,
        'fare': fare,
    }

    return render(request, 'admin/track_prices.html', context)

@login_required
def transaction_AT(request):
    
    records = TransportationRecord.objects.all()
    
    return render(request, 'admin/TransactionAT.html', {'records': records})

@login_required
def transaction_AC(request):
    
    records = CashierTransaction.objects.all()
    
    return render(request, 'admin/TransactionAC.html', {'records': records})

@login_required
def save_data(request):
    if request.method == "POST":
        # Get the data from the context
        date = request.POST.get('date')
        php_price = request.POST.get('php_price')
        usd_price = request.POST.get('usd_price')

        # Create a new DataCrawl instance and save it to the database
        data_crawl = DataCrawl(CrawlDate=date, CrawlPHP=php_price, CrawlUSD=usd_price)
        data_crawl.save()

        # Redirect back to the track_prices view or any other appropriate page
        return redirect('track_prices')
    else:
        # Handle GET requests to this view as needed
        pass

@login_required
def update_prices(request):
    if request.method == 'POST':
        # Get the new values for CurrentFare, CurrentDiesel, and CurrentSucceeding from the form
        new_farePUJ = request.POST.get('new_farePUJ')
        new_succeedingPUJ = request.POST.get('new_succeedingPUJ')
        new_fareBus = request.POST.get('new_fareBus')
        new_succeedingBus = request.POST.get('new_succeedingBus')        
        new_diesel = request.POST.get('new_diesel')
        

        # Query the database to get the CurrentPrice object with Num = 1
        current_price = CurrentPrice.objects.filter(Num=1).first()

        if current_price:
            # Check if the input values are not empty
            if new_farePUJ:
                current_price.CurrentFarePUJ = new_farePUJ
            if new_succeedingPUJ:
                current_price.CurrentSucceedingPUJ = new_succeedingPUJ
            if new_fareBus:
                current_price.CurrentFareBus = new_fareBus
            if new_succeedingBus:
                current_price.CurrentSucceedingBus = new_succeedingBus
            if new_diesel:
                current_price.CurrentDiesel = new_diesel

            # Set the CurrentDate to the current date
            current_price.CurrentDate = date.today()

            current_price.save()

            # Redirect to the track_prices view or any other appropriate page
            return redirect('track_prices')

    return render(request, 'admin/track_price.html')

@login_required
def update_current_price(request):
    if request.method == 'POST':
        # Retrieve the third and fourth calculation results from the POST data
        third_calculation_result = request.POST.get('third_calculation_result')
        fourth_calculation_result = request.POST.get('fourth_calculation_result')

        # Query the database to get the CurrentPrice object with Num=1
        current_price = CurrentPrice.objects.filter(Num=1).first()

        if current_price:
            # Update the CurrentFare and CurrentSucceeding fields
            if third_calculation_result:
                current_price.CurrentFare = float(third_calculation_result)
            if fourth_calculation_result:
                current_price.CurrentSucceeding = float(fourth_calculation_result)
            
            # Save the updated object
            current_price.save()

    return redirect('track_prices')


def round_to_quarter(value):
    return round(value * 4) / 4


def computing_update (request):
    # Check if the POST request contains the calculation values and save them
    if request.method == 'POST':
        third_calculation_result = request.POST.get('third_calculation_result')
        fourth_calculation_result = request.POST.get('fourth_calculation_result')
        fifth_calculation_result = request.POST.get('fifth_calculation_result')
        sixth_calculation_result = request.POST.get('sixth_calculation_result')
        php_price = request.POST.get('php_price')  # Retrieve php_price

        latest_price = CurrentPrice.objects.last()

        if third_calculation_result is not None:
            third_calculation_result = round_to_quarter(float(third_calculation_result))
            latest_price.CurrentFarePUJ = third_calculation_result

        if fourth_calculation_result is not None:
            fourth_calculation_result = round_to_quarter(float(fourth_calculation_result))
            latest_price.CurrentSucceedingPUJ = fourth_calculation_result

        if fifth_calculation_result is not None:
            fifth_calculation_result = round_to_quarter(float(fifth_calculation_result))
            latest_price.CurrentFareBus = fifth_calculation_result

        if sixth_calculation_result is not None:
            sixth_calculation_result = round_to_quarter(float(sixth_calculation_result))
            latest_price.CurrentSucceedingBus = sixth_calculation_result

        # Update the date to the current date and time
        latest_price.CurrentDate = timezone.now()

        # Update php_price if needed
        if php_price is not None:
            # Assuming php_price is a field in the CurrentPrice model
            latest_price.php_price = float(php_price)

        latest_price.save()
    return redirect('track_prices')
