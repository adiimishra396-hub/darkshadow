from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile


def home(request):
    return render(request, 'index.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    return render(request, 'login.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        phone = request.POST.get('phone_number', '').strip()
        age = request.POST.get('age', '').strip()
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        above_18 = request.POST.get('above_18')  # checkbox
        agree_terms = request.POST.get('agree_terms')  # checkbox

        # Validations
        if not above_18:
            messages.error(request, 'You must confirm you are 18 or above to register.')
            return render(request, 'signup.html', {'form_data': request.POST})
        if not agree_terms:
            messages.error(request, 'You must agree to our Terms & Conditions to register.')
            return render(request, 'signup.html', {'form_data': request.POST})
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html', {'form_data': request.POST})
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Please choose another.')
            return render(request, 'signup.html', {'form_data': request.POST})
        if UserProfile.objects.filter(phone_number=phone).exists():
            messages.error(request, 'This phone number is already registered.')
            return render(request, 'signup.html', {'form_data': request.POST})
        if int(age) < 18:
            messages.error(request, 'You must be at least 18 years old to register.')
            return render(request, 'signup.html', {'form_data': request.POST})

        # Create user
        user = User.objects.create_user(
            username=username,
            password=password1,
            first_name=first_name,
            last_name=last_name,
        )
        UserProfile.objects.create(
            user=user,
            last_name=last_name,
            age=int(age),
            phone_number=phone,
            is_above_18=True,
            agreed_to_terms=True,
        )
        messages.success(request, 'Account created! Please log in.')
        return redirect('login')

    return render(request, 'signup.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')
