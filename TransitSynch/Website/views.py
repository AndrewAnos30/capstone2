# django_project/users/views.py
from django.shortcuts import render, redirect
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
from django.core.mail import EmailMessage
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from .tokens import account_activation_token
from .models import DataCrawl
from django.db.models.query_utils import Q
from users.models import CustomUser

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

def  conductorHome(request):
   return render (request, 'conductor/conductorHome.html')

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

def commuter(request):


    return render(request, 'commuter/userHome.html')

def cashier(request):


    return render(request=request, template_name='cashier/cashierHome.html')

def conductor(request):

    return render(request=request, template_name='conductor/conductorHome.html')


#admin part
def admin(request):


    return render(request=request, template_name='admin/adminPage.html')




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
        template_name="admin/create_conductor.html",
        context={"form": form, "placeholders": placeholders}
    )



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
            user.UserGroup = "conductor"


            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('create_conductor')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = CashierRegistrationForm()

    return render(
        request=request,
        template_name="admin/create_cashier.html",
        context={"form": form, "placeholders": placeholders}
    )



def track_prices(request):
    url = "https://www.globalpetrolprices.com/Philippines/"
    result = requests.get(url)
    doc = BeautifulSoup(result.text,"html.parser")

    tags= doc.find_all("tr")
    parent = tags[2]
    prices = parent.find_all("td")
    
    # Extract the text content inside each <td> element
    extracted_data = [price.get_text(strip=True) for price in prices]

    # Organize the data into date, PHP price, and USD price
    date = extracted_data[0]
    php_price = extracted_data[1]
    usd_price = extracted_data[2]

    # Pass the organized data as context variables to the template
    context = {
        'date': date,
        'php_price': php_price,
        'usd_price': usd_price,
    }

    return render(request, 'admin/track_prices.html',context)

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

def inflation(request):
    url = "https://www.rateinflation.com/inflation-rate/philippines-inflation-rate/"
    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser")

    # Find the first div with class "css-in3yi3 e1x5eoea4"
    first_div = doc.find("div", class_="css-in3yi3 e1x5eoea4")

    # Find the first div with class "css-in3yi3 e1x5eoea5" after the first_div
    second_div = first_div.find_next("div", class_="css-in3yi3 e1x5eoea5")

    context = {
        'first_div': first_div.text if first_div else None,
        'second_div': second_div.text if second_div else None,
    }

    print("first_div:", first_div)  # Debug print
    print("second_div:", second_div)  # Debug print

    return render(request, 'admin/inflation.html', context)