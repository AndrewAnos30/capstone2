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
  # Get the user's IP location (latitude and longitude)
    ip_info = requests.get('https://ipinfo.io/json').json()
    loc = ip_info.get('loc', '').split(',')
    
    if len(loc) == 2:
        latitude, longitude = loc
        # Replace 'YOUR_BING_MAPS_API_KEY' with your actual Bing Maps API key
        bing_maps_api_key = 'An6l1TNT7us7PHNaVpOf7lud9ocQHllSrqXWovAkwYhFBj691ZXgQw2YELwQennz'
        
        # Use Bing Maps API to reverse geocode the coordinates
        bing_maps_url = f'https://dev.virtualearth.net/REST/v1/Locations/{latitude},{longitude}?o=json&key={bing_maps_api_key}'
        
        try:
            response = requests.get(bing_maps_url)
            if response.status_code == 200:
                data = response.json()
                location = data.get('resourceSets', [])[0].get('resources', [])[0].get('name', '')
            else:
                location = 'Location not found'
        except Exception as e:
            location = 'Error fetching location data'
    else:
        location = 'Location not available'
    
    return render(request, template_name='conductor/conductorHome.html', context={'location': location})

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

