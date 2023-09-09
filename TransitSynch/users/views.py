# django_project/users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import  login, logout, authenticate
import secrets
import string
import qrcode
from django.core.files.base import ContentFile
from io import BytesIO
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from. decorators import user_not_authenticated
from .forms import UserRegistrationForm, UserLoginForm

# Create your views here.
@user_not_authenticated
def registerCommuter(request):

    placeholders = {
        'contactNumber_placeholder': '09*********',
        'emergencyContact_placeholder': '09*********',
    }

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)  # Create the user object without saving it
            user.email = form.cleaned_data['email']
            
            # Generate a unique userSN
            userSN = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(20))
            user.userSN = userSN

            # Generate a QR code using userSN and save it to 'QR' field
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(userSN)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            user.QR.save(f'qr_{userSN}.png', ContentFile(buffer.getvalue()), save=False)

            user.save()
            login(request, user)
            messages.success(request, f"New Account created{user.username}")
            return redirect('/')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = UserRegistrationForm()

    return render(
        request=request,
        template_name="register.html",
        context={"form": form, "placeholders": placeholders}
    )


@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("home")

@user_not_authenticated
def custom_login(request):

    if request.method == 'POST':
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                messages.success(request, f"Hello <b>{user.username}</b>! You have been logged in")
                return redirect('home')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error) 

    form = UserLoginForm() 
    
    return render(
        request=request,
        template_name="login.html", 
        context={'form': form}
        )