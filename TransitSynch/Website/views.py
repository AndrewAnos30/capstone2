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
from .models import DataCrawl,CurrentPrice
from django.db.models.query_utils import Q
from users.models import CustomUser
from datetime import date
from .forms import KilometerForm
from math import ceil


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


# Create your views here.

def generate(request):
   return render (request, 'conductor/generate.html')


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
def cashier(request):


    return render(request=request, template_name='cashier/cashierHome.html')

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

            # Set UserGroup to "Commuter"
            user.UserGroup = "conductor"

            user.verified = True

            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('create_conductor')
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
            
            # Generate a unique userSN
            userSN = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(20))
            user.userSN = userSN

            # Set UserGroup to "Commuter"
            user.UserGroup = "cashier"

            user.verified = True

            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('create_cashier')
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