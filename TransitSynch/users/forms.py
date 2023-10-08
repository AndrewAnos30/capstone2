from django import forms
from django.core.validators import RegexValidator
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import PasswordResetForm


class UserRegistrationForm(UserCreationForm):


    phone_regex = RegexValidator(
        regex=r'^09\d{9}$',  # Matches "09" followed by 8 digits
        message="Phone number must be 11 digits and start with '09********'",
    )
    contactNumber = forms.CharField(validators=[phone_regex], max_length=11, required=False, widget=forms.TextInput(attrs={'placeholder': '09*********'}))
    emergencyContact = forms.CharField(validators=[phone_regex], max_length=11, required=False, widget=forms.TextInput(attrs={'placeholder': '09*********'}))
    email = forms.EmailField(help_text='A valid email address, please.', required=True)
    birthDate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    validID = forms.ImageField(required=False)  # Add this field for "valid ID" image upload


    graduation = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label='Graduation Date',
    )

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'middle_name', 'last_name', 'username', 'email', 'password1', 'password2',
                        'gender', 'age', 'birthDate', 'contactNumber', 'emergencyContact', 'contactPerson',
                        'status', 'graduation', 'validID', 'DPA']
        
        
    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    




class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username or Email'}),
        label="Username or Email*")

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))
    

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']


class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']



class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        attrs={'class': 'form-control', 'placeholder': 'Password'}
