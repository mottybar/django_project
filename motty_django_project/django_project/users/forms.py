from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Profile



def raise_error_validate_phone(phone, min_length):
    if (not phone.replace('-', '', 1).replace('+', '', 1).isdigit()):
        return ValidationError("Phone does not contain only digits")
    if len(phone) < min_length:
        return ValidationError("Phone is too short")



def raise_error_validate_name_chars_only(field, name):
    for char in field:
        if char.isdigit():
            return ValidationError(name + " cannot contain a digit")

def raise_error_validate_no_sql_injection(cleaned_data):
    validationerros={}
    for key, value in cleaned_data.items():
        if (type(value) is str and 'DROP TABLE' in value.upper()):  # TODO: Replace with a more general sql-injection test
            validationerros[key]=(ValidationError("Ooops, please don't try SQL Injection on "+key+" field"))
        elif (type(value) is str and 'SELECT * FROM' in value.upper()):  
            validationerros[key]=(ValidationError("Ooops, please don't try SQL Injection on "+key+" field"))
    return validationerros

class CustomAuthenticationForm(AuthenticationForm):


    def clean(self):
        error_dict = {}
        cd = self.cleaned_data
        sql_injection_error = raise_error_validate_no_sql_injection(cd)
        for key, value in sql_injection_error.items():
            error_dict[key] = value
        if error_dict:
            raise ValidationError(error_dict)
        return cd

    class Meta:
        model = User
        fields = ['username','password']


class UserRegisterForm(UserCreationForm):

    email = forms.EmailField()
    
    def clean(self):
        error_dict = {}
        cd = self.cleaned_data
        sql_injection_error = raise_error_validate_no_sql_injection(cd)
        for key, value in sql_injection_error.items():
            error_dict[key] = value
        if error_dict:
            raise ValidationError(error_dict)
        return cd


    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']


class CustomerRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    birth_date = forms.CharField(max_length=100)# TODO: Replace with date format + migrate
    join_date = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=100) # TODO: Check with Regular expression the format of phone
    monthly_discount = forms.IntegerField()
    pack_id = forms.IntegerField()



    def clean(self):
        error_dict = {}
        cd = self.cleaned_data


        if 'phone' in cd.keys():
            phone_error = raise_error_validate_phone(cd['phone'],10)
            if phone_error is not None:
                error_dict["phone"]= phone_error

        sql_injection_error = raise_error_validate_no_sql_injection(cd)
        for key,value in sql_injection_error.items():
            error_dict[key] = value


        if "first_name" in cd.keys():
            first_name_error = raise_error_validate_name_chars_only(cd["first_name"], "First name")
            if first_name_error is not None:
                error_dict["first_name"]= first_name_error

        if 'last_name' in cd.keys():
            last_name_error = raise_error_validate_name_chars_only(cd['last_name'], "Last name")
            if last_name_error is not None:
                error_dict["last_name"] = last_name_error

        if 'city' in cd.keys():
            city_error = raise_error_validate_name_chars_only(cd['city'], "City")
            if city_error is not None:
                error_dict["city"]=city_error

        if 'state' in cd.keys():
            state_error = raise_error_validate_name_chars_only(cd['state'], "State")
            if state_error is not None:
                error_dict["state"] = state_error
        # TODO: Another test
        if error_dict:
            raise ValidationError(error_dict)
        return cd
