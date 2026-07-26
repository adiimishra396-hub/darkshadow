from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from .models import UserProfile

# Hardcoded permanent admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_EMAIL = 'admin@gmail.com'
ADMIN_PASSWORD = '123456'


def home(request):
    return render(request, 'index.html')


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_panel')
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Always re-enforce admin password cannot be changed
            if user.is_superuser:
                # Ensure admin credentials are always the hardcoded ones
                if not user.check_password(ADMIN_PASSWORD):
                    user.set_password(ADMIN_PASSWORD)
                    user.save()
                login(request, user)
                return redirect('admin_panel')
            else:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}! 🎉')
                return redirect('home')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    return render(request, 'login.html')


def signup_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_panel')
        return redirect('home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        phone = request.POST.get('phone_number', '').strip()
        age = request.POST.get('age', '').strip()
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        above_18 = request.POST.get('above_18')
        agree_terms = request.POST.get('agree_terms')

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
        if not age.isdigit() or int(age) < 18:
            messages.error(request, 'You must be at least 18 years old to register.')
            return render(request, 'signup.html', {'form_data': request.POST})

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
        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login')

    return render(request, 'signup.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def admin_panel_view(request):
    """Custom admin panel — superuser only."""
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, 'Access denied. Admins only.')
        return redirect('login')

    # Always enforce permanent admin credentials (prevent changes from Django admin)
    admin_user = User.objects.filter(username=ADMIN_USERNAME).first()
    if admin_user and not admin_user.check_password(ADMIN_PASSWORD):
        admin_user.set_password(ADMIN_PASSWORD)
        admin_user.email = ADMIN_EMAIL
        admin_user.save()

    # Get all signups (non-superusers) with their profiles
    users = User.objects.filter(is_superuser=False).order_by('-date_joined').select_related('profile')

    user_data = []
    for u in users:
        profile = getattr(u, 'profile', None)
        user_data.append({
            'id': u.id,
            'username': u.username,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email or '—',
            'phone': profile.phone_number if profile else '—',
            'age': profile.age if profile else '—',
            'date_joined': u.date_joined,
            'is_active': u.is_active,
        })

    context = {
        'user_data': user_data,
        'total_users': len(user_data),
        'admin_username': ADMIN_USERNAME,
        'admin_email': ADMIN_EMAIL,
        'admin_password': ADMIN_PASSWORD,
    }
    return render(request, 'admin_panel.html', context)


def admin_info_view(request):
    return render(request, 'admin_login.html')
