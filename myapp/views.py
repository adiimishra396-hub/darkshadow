from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import OperationalError
from django.db.models import Sum
from decimal import Decimal
from .models import UserProfile, Payment, Wallet, WalletTransaction

ADMIN_USERNAME = 'admin'
ADMIN_EMAIL    = 'admin@gmail.com'
ADMIN_PASSWORD = '123456'


def _ensure_admin():
    """Guarantee permanent admin account exists with fixed credentials."""
    user, created = User.objects.get_or_create(
        username=ADMIN_USERNAME,
        defaults={'email': ADMIN_EMAIL, 'is_staff': True, 'is_superuser': True}
    )
    user.email = ADMIN_EMAIL
    user.is_staff = True
    user.is_superuser = True
    user.set_password(ADMIN_PASSWORD)
    user.save()
    return user


def _get_or_create_wallet(user):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet


# ─────────────────────────── Home ─────────────────────────────────────────────
def home(request):
    return render(request, 'index.html')


# ─────────────────────────── Login ────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('admin_panel' if request.user.is_superuser else 'home')

    _ensure_admin()

    if request.method == 'POST':
        login_type = request.POST.get('login_type', 'email').strip()
        password   = request.POST.get('password', '').strip()
        user       = None

        if login_type == 'email':
            email = request.POST.get('email', '').strip().lower()
            if not email:
                messages.error(request, 'Please enter your email address.')
                return render(request, 'login.html')
            try:
                matched = User.objects.get(email__iexact=email)
                user = authenticate(request, username=matched.username, password=password)
            except User.DoesNotExist:
                user = None
            except User.MultipleObjectsReturned:
                matched = User.objects.filter(email__iexact=email).first()
                user = authenticate(request, username=matched.username, password=password) if matched else None
        else:
            username = request.POST.get('username', '').strip()
            if not username:
                messages.error(request, 'Please enter your username.')
                return render(request, 'login.html')
            user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_panel')
            messages.success(request, f'Welcome back, {user.first_name or user.username}! 🎉')
            return redirect('home')

        messages.error(request, 'Invalid credentials. Please check and try again.')

    return render(request, 'login.html')


# ─────────────────────────── Signup ───────────────────────────────────────────
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('admin_panel' if request.user.is_superuser else 'home')
    if request.method == 'POST':
        first_name  = request.POST.get('first_name', '').strip()
        last_name   = request.POST.get('last_name', '').strip()
        username    = request.POST.get('username', '').strip()
        phone       = request.POST.get('phone_number', '').strip()
        age         = request.POST.get('age', '').strip()
        password1   = request.POST.get('password1')
        password2   = request.POST.get('password2')
        above_18    = request.POST.get('above_18')
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

        user = User.objects.create_user(username=username, password=password1,
                                        first_name=first_name, last_name=last_name)
        UserProfile.objects.create(user=user, last_name=last_name, age=int(age),
                                   phone_number=phone, is_above_18=True, agreed_to_terms=True)
        Wallet.objects.create(user=user)
        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('login')
    return render(request, 'signup.html')


# ─────────────────────────── Logout ───────────────────────────────────────────
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


# ─────────────────────────── Wallet: Add Money ────────────────────────────────
def add_money_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_superuser:
        return redirect('admin_panel')

    wallet = _get_or_create_wallet(request.user)

    if request.method == 'POST':
        amount_str = request.POST.get('amount', '').strip()
        method     = request.POST.get('method', 'upi').strip()
        try:
            amount = Decimal(amount_str)
            if amount <= 0:
                raise ValueError
        except Exception:
            messages.error(request, 'Please enter a valid amount greater than ₹0.')
            return render(request, 'add_money.html', {'wallet': wallet})

        if amount > Decimal('100000'):
            messages.error(request, 'Maximum single deposit is ₹1,00,000.')
            return render(request, 'add_money.html', {'wallet': wallet})

        wallet.balance += amount
        wallet.save()
        WalletTransaction.objects.create(
            wallet=wallet, amount=amount, txn_type='credit',
            description=f'Added via {method.upper()}')

        import uuid
        try:
            Payment.objects.create(
                user=request.user, amount=amount, status='success',
                method=method, transaction_id=str(uuid.uuid4())[:20],
                description='Wallet top-up')
        except OperationalError:
            pass  # Payment table not yet migrated — skip gracefully

        messages.success(request, f'₹{amount} added to your wallet successfully! 🎉')
        return redirect('my_wallet')

    return render(request, 'add_money.html', {'wallet': wallet})


# ─────────────────────────── Wallet: My Wallet ────────────────────────────────
def my_wallet_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_superuser:
        return redirect('admin_panel')

    wallet = _get_or_create_wallet(request.user)
    transactions = wallet.transactions.all()[:20]
    total_credited = wallet.transactions.filter(txn_type='credit').aggregate(s=Sum('amount'))['s'] or 0
    total_debited  = wallet.transactions.filter(txn_type='debit').aggregate(s=Sum('amount'))['s'] or 0

    context = {
        'wallet': wallet,
        'transactions': transactions,
        'total_credited': total_credited,
        'total_debited': total_debited,
    }
    return render(request, 'my_wallet.html', context)


# ─────────────────────────── Edit Profile ─────────────────────────────────────
def edit_profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_superuser:
        return redirect('admin_panel')

    user    = request.user
    profile = getattr(user, 'profile', None)

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip()
        phone      = request.POST.get('phone_number', '').strip()
        age        = request.POST.get('age', '').strip()

        if not first_name:
            messages.error(request, 'First name is required.')
            return render(request, 'edit_profile.html', {'user': user, 'profile': profile})
        if not age.isdigit() or int(age) < 18:
            messages.error(request, 'Age must be 18 or above.')
            return render(request, 'edit_profile.html', {'user': user, 'profile': profile})
        if profile and UserProfile.objects.filter(phone_number=phone).exclude(pk=profile.pk).exists():
            messages.error(request, 'This phone number is already used by another account.')
            return render(request, 'edit_profile.html', {'user': user, 'profile': profile})

        user.first_name = first_name
        user.last_name  = last_name
        user.email      = email
        user.save()

        if profile:
            profile.last_name    = last_name
            profile.age          = int(age)
            profile.phone_number = phone
            profile.save()

        messages.success(request, 'Profile updated successfully! ✅')
        return redirect('edit_profile')

    return render(request, 'edit_profile.html', {'user': user, 'profile': profile})


# ─────────────────────────── Change Password ──────────────────────────────────
def change_password_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_superuser:
        return redirect('admin_panel')

    if request.method == 'POST':
        current = request.POST.get('current_password', '')
        new1    = request.POST.get('new_password1', '')
        new2    = request.POST.get('new_password2', '')

        if not request.user.check_password(current):
            messages.error(request, 'Current password is incorrect.')
            return render(request, 'change_password.html')
        if len(new1) < 6:
            messages.error(request, 'New password must be at least 6 characters.')
            return render(request, 'change_password.html')
        if new1 != new2:
            messages.error(request, 'New passwords do not match.')
            return render(request, 'change_password.html')
        if current == new1:
            messages.error(request, 'New password must be different from current password.')
            return render(request, 'change_password.html')

        request.user.set_password(new1)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, 'Password changed successfully! 🔐')
        return redirect('change_password')

    return render(request, 'change_password.html')


# ─────────────────────────── Admin Panel ──────────────────────────────────────
def admin_panel_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, 'Access denied. Admins only.')
        return redirect('login')

    _ensure_admin()

    users = User.objects.filter(is_superuser=False).order_by('-date_joined').select_related('profile')
    user_data = []
    for u in users:
        profile = getattr(u, 'profile', None)
        user_data.append({
            'id': u.id, 'username': u.username,
            'first_name': u.first_name, 'last_name': u.last_name,
            'email': u.email or '—', 'phone': profile.phone_number if profile else '—',
            'age': profile.age if profile else '—',
            'date_joined': u.date_joined, 'is_active': u.is_active,
        })

    # Safe payment queries — handle case where table doesn't exist yet
    try:
        payments       = Payment.objects.select_related('user').order_by('-created_at')
        total_revenue  = payments.filter(status='success').aggregate(s=Sum('amount'))['s'] or 0
        total_pending  = payments.filter(status='pending').aggregate(s=Sum('amount'))['s'] or 0
        payments_count = payments.count()
        success_count  = payments.filter(status='success').count()
        payments_list  = list(payments[:50])
    except OperationalError:
        # Table hasn't been created yet on this deploy — show empty state
        payments_list  = []
        total_revenue  = 0
        total_pending  = 0
        payments_count = 0
        success_count  = 0

    context = {
        'user_data': user_data,
        'total_users': len(user_data),
        'admin_username': ADMIN_USERNAME,
        'admin_email': ADMIN_EMAIL,
        'admin_password': ADMIN_PASSWORD,
        'payments': payments_list,
        'total_revenue': total_revenue,
        'total_pending': total_pending,
        'payments_count': payments_count,
        'success_count': success_count,
    }
    return render(request, 'admin_panel.html', context)


def admin_info_view(request):
    return render(request, 'admin_login.html')
