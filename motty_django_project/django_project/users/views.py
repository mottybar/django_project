from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, CustomerRegistrationForm,CustomAuthenticationForm
from .models import Customer
from django.utils.html import format_html




def login_request(request):
    message = format_html('<li>Please enter a correct username and password. Note that both fields may be case-sensitive.</li>')
    if request.method == 'POST':
        form = CustomAuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password,request=request)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}")
                return redirect('/')
            else:
                messages.error(request, message,extra_tags='danger')
        else:
            messages.error(request, message,extra_tags='danger')
            return render(request, 'users/login.html', {'form': form})

    form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required()
def customers(request):
    if request.method == 'POST':        # If user added new customer
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            new_customer =  Customer(   first_name = form.cleaned_data['first_name'],
                                        last_name = form.cleaned_data['last_name'],
                                        birth_date = form.cleaned_data['birth_date'],
                                        join_date = form.cleaned_data['join_date'],
                                        city = form.cleaned_data['city'],
                                        state = form.cleaned_data['state'],
                                        phone = form.cleaned_data['phone'],
                                        monthly_discount = form.cleaned_data['monthly_discount'],
                                        pack_id = form.cleaned_data['pack_id'])
            new_customer.save()
            form = CustomerRegistrationForm()

    else:        # If user just opened the customers page - we give him an empty page
        form = CustomerRegistrationForm()

    list_of_customers = Customer.objects.all()
    return render(request, 'users/customers.html', {'customers': list_of_customers, 'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)

