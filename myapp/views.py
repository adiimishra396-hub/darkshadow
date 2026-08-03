from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import OperationalError, transaction
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from .models import (
    UserProfile, Payment, Wallet, WalletTransaction,
    SpinWallet, SpinPurchase, RazorpaySettings, SpinMachineSettings,
    CoinFlipSettings, CoinFlipBet, DiceSettings, DiceBet,
    CardHighLowSettings, CardHighLowRound,
    AndarBaharSettings, AndarBaharBet, RouletteSettings, RouletteBet,
    SicBoSettings, SicBoBet,
)
import razorpay
import os
import json
import hmac
import hashlib
import secrets

ADMIN_USERNAME = 'admin'
ADMIN_EMAIL    = 'admin@gmail.com'
ADMIN_PASSWORD = '123456'


# ── Key resolution: DB → env vars ──────────────────────────────────────────────
def get_razorpay_keys():
    try:
        cfg = RazorpaySettings.get_singleton()
        key_id     = cfg.key_id.strip()
        key_secret = cfg.key_secret.strip()
    except Exception:
        key_id = key_secret = ''
    if not key_id:
        key_id = os.environ.get('RAZORPAY_KEY_ID', '')
    if not key_secret:
        key_secret = os.environ.get('RAZORPAY_KEY_SECRET', '')
    return key_id, key_secret


def get_spin_settings():
    """Returns the SpinMachineSettings singleton. Safe fallback if table missing."""
    try:
        return SpinMachineSettings.get_singleton()
    except Exception:
        class _Defaults:
            spin_pack_spins          = 3
            spin_pack_amount         = Decimal('10.00')
            homepage_jackpot_display = '84,52,910'
            is_active                = True
        return _Defaults()


def get_coinflip_settings():
    """Returns the CoinFlipSettings singleton. Safe fallback if table missing."""
    try:
        return CoinFlipSettings.get_singleton()
    except Exception:
        class _Defaults:
            win_multiplier = Decimal('1.90')
            min_bet        = Decimal('10.00')
            max_bet        = Decimal('5000.00')
            is_active      = True
        return _Defaults()


def get_dice_settings():
    """Returns the DiceSettings singleton. Safe fallback if table missing."""
    try:
        return DiceSettings.get_singleton()
    except Exception:
        class _Defaults:
            house_edge_percent = Decimal('5.00')
            min_bet            = Decimal('10.00')
            max_bet            = Decimal('5000.00')
            is_active          = True
        return _Defaults()


def get_cardhilo_settings():
    """Returns the CardHighLowSettings singleton. Safe fallback if table missing."""
    try:
        return CardHighLowSettings.get_singleton()
    except Exception:
        class _Defaults:
            house_edge_percent = Decimal('5.00')
            min_bet            = Decimal('10.00')
            max_bet            = Decimal('5000.00')
            is_active          = True
        return _Defaults()


def get_andarbahar_settings():
    """Returns the AndarBaharSettings singleton. Safe fallback if table missing."""
    try:
        return AndarBaharSettings.get_singleton()
    except Exception:
        class _Defaults:
            win_multiplier = Decimal('1.90')
            min_bet        = Decimal('10.00')
            max_bet        = Decimal('5000.00')
            is_active      = True
        return _Defaults()


def get_roulette_settings():
    """Returns the RouletteSettings singleton. Safe fallback if table missing."""
    try:
        return RouletteSettings.get_singleton()
    except Exception:
        class _Defaults:
            house_edge_percent = Decimal('5.00')
            min_bet            = Decimal('10.00')
            max_bet            = Decimal('5000.00')
            is_active          = True
        return _Defaults()


def get_sicbo_settings():
    """Returns the SicBoSettings singleton. Safe fallback if table missing."""
    try:
        return SicBoSettings.get_singleton()
    except Exception:
        class _Defaults:
            house_edge_percent = Decimal('5.00')
            min_bet            = Decimal('10.00')
            max_bet            = Decimal('5000.00')
            is_active          = True
        return _Defaults()


# ── Admin bootstrap ─────────────────────────────────────────────────────────────
def _ensure_admin():
    user, created = User.objects.get_or_create(
        username=ADMIN_USERNAME,
        defaults={
            'email': ADMIN_EMAIL,
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
            'first_name': 'Admin',
        }
    )
    changed = False
    if user.email != ADMIN_EMAIL:      user.email = ADMIN_EMAIL;           changed = True
    if not user.is_staff:              user.is_staff = True;               changed = True
    if not user.is_superuser:          user.is_superuser = True;           changed = True
    if not user.is_active:             user.is_active = True;              changed = True
    if user.first_name != 'Admin':     user.first_name = 'Admin';          changed = True
    if not user.check_password(ADMIN_PASSWORD):
        user.set_password(ADMIN_PASSWORD); changed = True
    if changed:
        user.save()
    return user


def _get_or_create_wallet(user):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet


def _get_or_create_spin_wallet(user):
    sw, _ = SpinWallet.objects.get_or_create(user=user)
    return sw


# ── Home ───────────────────────────────────────────────────────────────────────
def home(request):
    spin_wallet = None
    wallet      = None
    if request.user.is_authenticated and not request.user.is_superuser:
        spin_wallet = _get_or_create_spin_wallet(request.user)
        wallet      = _get_or_create_wallet(request.user)
    key_id, _ = get_razorpay_keys()
    spin_cfg      = get_spin_settings()
    coinflip_cfg  = get_coinflip_settings()
    dice_cfg      = get_dice_settings()
    cardhilo_cfg  = get_cardhilo_settings()
    andarbahar_cfg = get_andarbahar_settings()
    roulette_cfg   = get_roulette_settings()
    sicbo_cfg      = get_sicbo_settings()
    return render(request, 'index.html', {
        'spin_wallet':              spin_wallet,
        'wallet':                   wallet,
        'razorpay_key_id':          key_id,
        'spin_pack_amount':         spin_cfg.spin_pack_amount,
        'spin_pack_spins':          spin_cfg.spin_pack_spins,
        'spin_machine_active':      spin_cfg.is_active,
        'homepage_jackpot_display': spin_cfg.homepage_jackpot_display,
        'coinflip_active':          coinflip_cfg.is_active,
        'coinflip_min_bet':         coinflip_cfg.min_bet,
        'coinflip_max_bet':         coinflip_cfg.max_bet,
        'coinflip_win_multiplier':  coinflip_cfg.win_multiplier,
        'dice_active':              dice_cfg.is_active,
        'dice_min_bet':             dice_cfg.min_bet,
        'dice_max_bet':             dice_cfg.max_bet,
        'dice_house_edge':          dice_cfg.house_edge_percent,
        'cardhilo_active':          cardhilo_cfg.is_active,
        'cardhilo_min_bet':         cardhilo_cfg.min_bet,
        'cardhilo_max_bet':         cardhilo_cfg.max_bet,
        'cardhilo_house_edge':      cardhilo_cfg.house_edge_percent,
        'andarbahar_active':          andarbahar_cfg.is_active,
        'andarbahar_min_bet':         andarbahar_cfg.min_bet,
        'andarbahar_max_bet':         andarbahar_cfg.max_bet,
        'andarbahar_win_multiplier':  andarbahar_cfg.win_multiplier,
        'roulette_active':            roulette_cfg.is_active,
        'roulette_min_bet':           roulette_cfg.min_bet,
        'roulette_max_bet':           roulette_cfg.max_bet,
        'roulette_house_edge':        roulette_cfg.house_edge_percent,
        'sicbo_active':               sicbo_cfg.is_active,
        'sicbo_min_bet':              sicbo_cfg.min_bet,
        'sicbo_max_bet':              sicbo_cfg.max_bet,
        'sicbo_house_edge':           sicbo_cfg.house_edge_percent,
    })


# ── Login ──────────────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'GET':
        _ensure_admin()
    if request.method == 'POST':
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '').strip()
        user     = None
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
        if user is not None:
            if not user.is_active:
                messages.error(request, 'Your account has been disabled. Please contact support.')
                return render(request, 'login.html')
            login(request, user)
            if user.is_superuser:
                messages.success(request, 'Welcome back, Admin! 🛡️')
            else:
                name = user.first_name or user.username
                messages.success(request, f'Welcome back, {name}! 🎉 You are now logged in.')
            return redirect('home')
        messages.error(request, 'Invalid credentials. Please check your email and password.')
    return render(request, 'login.html')


# ── Signup ─────────────────────────────────────────────────────────────────────
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        first_name  = request.POST.get('first_name', '').strip()
        last_name   = request.POST.get('last_name', '').strip()
        email       = request.POST.get('email', '').strip().lower()
        phone       = request.POST.get('phone_number', '').strip()
        age         = request.POST.get('age', '').strip()
        password1   = request.POST.get('password1', '')
        password2   = request.POST.get('password2', '')
        above_18    = request.POST.get('above_18')
        agree_terms = request.POST.get('agree_terms')
        if not first_name:
            messages.error(request, 'First name is required.')
            return render(request, 'signup.html', {'form_data': request.POST})
        if not email:
            messages.error(request, 'Email address is required.')
            return render(request, 'signup.html', {'form_data': request.POST})
        if not above_18:
            messages.error(request, 'You must confirm you are 18 or above to register.')
            return render(request, 'signup.html', {'form_data': request.POST})
        if not agree_terms:
            messages.error(request, 'You must agree to our Terms & Conditions to register.')
            return render(request, 'signup.html', {'form_data': request.POST})
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html', {'form_data': request.POST})
        if len(password1) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'signup.html', {'form_data': request.POST})
        if not age.isdigit() or int(age) < 18:
            messages.error(request, 'You must be at least 18 years old to register.')
            return render(request, 'signup.html', {'form_data': request.POST})
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'An account with this email already exists. Please log in.')
            return render(request, 'signup.html', {'form_data': request.POST})
        if phone and UserProfile.objects.filter(phone_number=phone).exists():
            messages.error(request, 'This phone number is already registered.')
            return render(request, 'signup.html', {'form_data': request.POST})
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username__iexact=username).exists():
            username = f'{base_username}{counter}'
            counter += 1
        user = User.objects.create_user(
            username=username, password=password1, email=email,
            first_name=first_name, last_name=last_name,
        )
        UserProfile.objects.create(
            user=user, last_name=last_name, age=int(age),
            phone_number=phone, is_above_18=True, agreed_to_terms=True,
        )
        Wallet.objects.create(user=user)
        SpinWallet.objects.create(user=user)
        messages.success(request, f'Account created successfully! Welcome to Darkshadow, {first_name}! 🎉 Please log in.')
        return redirect('login')
    return render(request, 'signup.html')


# ── Logout ─────────────────────────────────────────────────────────────────────
def logout_view(request):
    name = request.user.first_name or request.user.username if request.user.is_authenticated else 'Player'
    logout(request)
    messages.success(request, f'Goodbye, {name}! You have been logged out. See you soon! 👋')
    return redirect('home')


# ── Add Money (page render) ────────────────────────────────────────────────────
def add_money_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to add money.')
        return redirect('login')
    if request.user.is_superuser:
        return redirect('admin_panel')
    wallet = _get_or_create_wallet(request.user)
    key_id, _ = get_razorpay_keys()
    return render(request, 'add_money.html', {
        'wallet': wallet,
        'razorpay_key_id': key_id,
        'razorpay_configured': bool(key_id),
        'user': request.user,
    })


# ── Wallet: Create Razorpay Order ──────────────────────────────────────────────
@require_POST
def wallet_create_order(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    if request.user.is_superuser:
        return JsonResponse({'error': 'Admins cannot add money to wallet'}, status=403)
    key_id, key_secret = get_razorpay_keys()
    if not key_id or not key_secret:
        return JsonResponse({'error': 'Payment gateway not configured. Please contact admin.'}, status=503)
    try:
        data   = json.loads(request.body)
        amount = float(data.get('amount', 0))
        method = data.get('method', 'upi')
        if amount <= 0:
            return JsonResponse({'error': 'Amount must be greater than ₹0'}, status=400)
        if amount > 100000:
            return JsonResponse({'error': 'Maximum single deposit is ₹1,00,000'}, status=400)
        valid_methods = ['upi', 'card', 'netbanking', 'wallet', 'other']
        if method not in valid_methods:
            method = 'upi'
        client = razorpay.Client(auth=(key_id, key_secret))
        amount_paise = int(amount * 100)
        order = client.order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'payment_capture': 1,
            'notes': {
                'user_id': str(request.user.id),
                'method': method,
                'description': 'Wallet top-up',
            }
        })
        Payment.objects.create(
            user=request.user,
            amount=Decimal(str(amount)),
            status='pending',
            method=method,
            transaction_id=order['id'],
            description='Wallet top-up via Razorpay',
        )
        return JsonResponse({
            'order_id': order['id'],
            'amount':   amount_paise,
            'currency': 'INR',
            'key_id':   key_id,
            'name':     request.user.first_name or request.user.username,
            'email':    request.user.email,
            'method':   method,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ── Wallet: Verify Payment & Credit ───────────────────────────────────────────
@require_POST
def wallet_verify_payment(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    _, key_secret = get_razorpay_keys()
    if not key_secret:
        return JsonResponse({'success': False, 'error': 'Payment gateway not configured'}, status=503)
    try:
        data = json.loads(request.body)
        razorpay_order_id   = data.get('razorpay_order_id', '')
        razorpay_payment_id = data.get('razorpay_payment_id', '')
        razorpay_signature  = data.get('razorpay_signature', '')
        msg      = f"{razorpay_order_id}|{razorpay_payment_id}"
        expected = hmac.new(key_secret.encode(), msg.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, razorpay_signature):
            return JsonResponse({'success': False, 'error': 'Invalid payment signature'}, status=400)
        payment = Payment.objects.filter(
            user=request.user, transaction_id=razorpay_order_id, status='pending'
        ).first()
        if not payment:
            return JsonResponse({'success': False, 'error': 'Payment record not found'}, status=404)
        payment.status = 'success'
        payment.save()
        wallet = _get_or_create_wallet(request.user)
        wallet.balance += payment.amount
        wallet.save()
        WalletTransaction.objects.create(
            wallet=wallet, amount=payment.amount, txn_type='credit',
            description=f'Added via {payment.method.upper()} (Razorpay • {razorpay_payment_id})',
        )
        return JsonResponse({
            'success':         True,
            'amount_credited': float(payment.amount),
            'new_balance':     float(wallet.balance),
            'message':         f'🎉 ₹{payment.amount} added to your wallet successfully!',
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ── My Wallet ──────────────────────────────────────────────────────────────────
def my_wallet_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to view your wallet.')
        return redirect('login')
    if request.user.is_superuser:
        return redirect('admin_panel')
    wallet = _get_or_create_wallet(request.user)
    transactions   = wallet.transactions.all()[:20]
    total_credited = wallet.transactions.filter(txn_type='credit').aggregate(s=Sum('amount'))['s'] or 0
    total_debited  = wallet.transactions.filter(txn_type='debit').aggregate(s=Sum('amount'))['s'] or 0
    return render(request, 'my_wallet.html', {
        'wallet': wallet, 'transactions': transactions,
        'total_credited': total_credited, 'total_debited': total_debited,
    })


# ── Edit Profile ───────────────────────────────────────────────────────────────
def edit_profile_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to edit your profile.')
        return redirect('login')
    if request.user.is_superuser:
        return redirect('admin_panel')
    user    = request.user
    profile = getattr(user, 'profile', None)
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip().lower()
        phone      = request.POST.get('phone_number', '').strip()
        age        = request.POST.get('age', '').strip()
        if not first_name:
            messages.error(request, 'First name is required.')
            return render(request, 'edit_profile.html', {'user': user, 'profile': profile})
        if not age.isdigit() or int(age) < 18:
            messages.error(request, 'Age must be 18 or above.')
            return render(request, 'edit_profile.html', {'user': user, 'profile': profile})
        if email and User.objects.filter(email__iexact=email).exclude(pk=user.pk).exists():
            messages.error(request, 'This email is already in use by another account.')
            return render(request, 'edit_profile.html', {'user': user, 'profile': profile})
        if profile and phone and UserProfile.objects.filter(phone_number=phone).exclude(pk=profile.pk).exists():
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


# ── Change Password ────────────────────────────────────────────────────────────
def change_password_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to change your password.')
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
            messages.error(request, 'New password must be different from your current password.')
            return render(request, 'change_password.html')
        request.user.set_password(new1)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, 'Password changed successfully! 🔐')
        return redirect('change_password')
    return render(request, 'change_password.html')


# ── Admin Panel ────────────────────────────────────────────────────────────────
def admin_panel_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, 'Access denied. Admins only.')
        return redirect('login')
    users = User.objects.filter(is_superuser=False).order_by('-date_joined').select_related('profile')
    user_data = []
    for u in users:
        profile = getattr(u, 'profile', None)
        user_data.append({
            'id':          u.id,
            'username':    u.username,
            'first_name':  u.first_name,
            'last_name':   u.last_name,
            'email':       u.email or '—',
            'phone':       profile.phone_number if profile else '—',
            'age':         profile.age if profile else '—',
            'date_joined': u.date_joined,
            'is_active':   u.is_active,
        })
    try:
        payments       = Payment.objects.select_related('user').order_by('-created_at')
        total_revenue  = payments.filter(status='success').aggregate(s=Sum('amount'))['s'] or 0
        total_pending  = payments.filter(status='pending').aggregate(s=Sum('amount'))['s'] or 0
        payments_count = payments.count()
        success_count  = payments.filter(status='success').count()
        payments_list  = list(payments[:50])
    except OperationalError:
        payments_list  = []
        total_revenue  = total_pending = payments_count = success_count = 0

    # Spin Machine stats
    try:
        spin_purchases       = SpinPurchase.objects.select_related('user').order_by('-created_at')
        spin_total_revenue   = spin_purchases.filter(status='success').aggregate(s=Sum('amount'))['s'] or 0
        spin_total_spins_sold = spin_purchases.filter(status='success').aggregate(s=Sum('spins_purchased'))['s'] or 0
        spin_unique_buyers   = spin_purchases.filter(status='success').values('user').distinct().count()
        spin_purchases_count = spin_purchases.filter(status='success').count()
        spin_recent          = list(spin_purchases[:10])
    except OperationalError:
        spin_total_revenue = spin_total_spins_sold = spin_unique_buyers = spin_purchases_count = 0
        spin_recent = []

    # Razorpay settings
    try:
        rzp_settings = RazorpaySettings.get_singleton()
    except Exception:
        rzp_settings = None
    key_id, _ = get_razorpay_keys()

    # Spin machine settings
    spin_cfg = get_spin_settings()

    return render(request, 'admin_panel.html', {
        'user_data':             user_data,
        'total_users':           len(user_data),
        'admin_username':        ADMIN_USERNAME,
        'admin_email':           ADMIN_EMAIL,
        'admin_password':        ADMIN_PASSWORD,
        'payments':              payments_list,
        'total_revenue':         total_revenue,
        'total_pending':         total_pending,
        'payments_count':        payments_count,
        'success_count':         success_count,
        'rzp_settings':          rzp_settings,
        'razorpay_configured':   bool(key_id),
        # Spin machine
        'spin_cfg':              spin_cfg,
        'spin_total_revenue':    spin_total_revenue,
        'spin_total_spins_sold': spin_total_spins_sold,
        'spin_unique_buyers':    spin_unique_buyers,
        'spin_purchases_count':  spin_purchases_count,
        'spin_recent':           spin_recent,
    })


# ── Admin: Save Razorpay Settings ──────────────────────────────────────────────
@require_POST
def save_razorpay_settings(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('login')
    key_id     = request.POST.get('rzp_key_id', '').strip()
    key_secret = request.POST.get('rzp_key_secret', '').strip()
    if not key_id or not key_secret:
        messages.error(request, 'Both Key ID and Key Secret are required.')
        return redirect('admin_panel')
    cfg = RazorpaySettings.get_singleton()
    cfg.key_id     = key_id
    cfg.key_secret = key_secret
    cfg.save()
    messages.success(request, '✅ Razorpay settings saved successfully! Payments are now live.')
    return redirect('admin_panel')


# ── Admin: Save Spin Machine Settings ─────────────────────────────────────────
@require_POST
def save_spin_settings(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('login')
    try:
        cfg = SpinMachineSettings.get_singleton()
        cfg.spin_pack_spins  = int(request.POST.get('spin_pack_spins', 3))
        cfg.spin_pack_amount = Decimal(request.POST.get('spin_pack_amount', '10.00'))
        cfg.homepage_jackpot_display = request.POST.get('homepage_jackpot_display', '84,52,910').strip()
        cfg.is_active        = request.POST.get('is_active') == 'on'
        if cfg.spin_pack_spins < 1:
            raise ValueError('Spins per pack must be at least 1')
        if cfg.spin_pack_amount <= 0:
            raise ValueError('Pack price must be greater than ₹0')
        cfg.save()
        messages.success(request, '✅ Spin machine settings saved! Frontend is now live with new values.')
    except Exception as e:
        messages.error(request, f'Error saving spin settings: {e}')
    return redirect('admin_panel')


# ── Admin: Toggle User Active ──────────────────────────────────────────────────
def toggle_user_active(request, user_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('login')
    if request.method == 'POST':
        u = get_object_or_404(User, pk=user_id, is_superuser=False)
        u.is_active = not u.is_active
        u.save()
        state = 'activated' if u.is_active else 'deactivated'
        messages.success(request, f'User @{u.username} has been {state}.')
    return redirect('admin_panel')


# ── Admin: Delete User ─────────────────────────────────────────────────────────
def delete_user(request, user_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('login')
    if request.method == 'POST':
        u = get_object_or_404(User, pk=user_id, is_superuser=False)
        username = u.username
        u.delete()
        messages.success(request, f'User @{username} has been permanently deleted.')
    return redirect('admin_panel')


# ── Admin: Add User Manually ───────────────────────────────────────────────────
def admin_add_user(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('login')
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip().lower()
        phone      = request.POST.get('phone_number', '').strip()
        age        = request.POST.get('age', '').strip()
        password   = request.POST.get('password', '')
        if not first_name:
            messages.error(request, 'First name is required.')
            return redirect('admin_panel')
        if not email:
            messages.error(request, 'Email is required.')
            return redirect('admin_panel')
        if not password or len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return redirect('admin_panel')
        if not age.isdigit() or int(age) < 18:
            messages.error(request, 'Age must be a number ≥ 18.')
            return redirect('admin_panel')
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, f'A user with email {email} already exists.')
            return redirect('admin_panel')
        if phone and UserProfile.objects.filter(phone_number=phone).exists():
            messages.error(request, 'This phone number is already registered.')
            return redirect('admin_panel')
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username__iexact=username).exists():
            username = f'{base_username}{counter}'
            counter += 1
        user = User.objects.create_user(
            username=username, password=password, email=email,
            first_name=first_name, last_name=last_name,
        )
        UserProfile.objects.create(
            user=user, last_name=last_name, age=int(age),
            phone_number=phone, is_above_18=True, agreed_to_terms=True,
        )
        Wallet.objects.create(user=user)
        SpinWallet.objects.create(user=user)
        messages.success(request, f'✅ User {first_name} {last_name} (@{username}) created successfully!')
    return redirect('admin_panel')


def admin_info_view(request):
    return render(request, 'admin_login.html')


# ── Jackpot: Create Razorpay Order ─────────────────────────────────────────────
@require_POST
def jackpot_create_order(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    if request.user.is_superuser:
        return JsonResponse({'error': 'Admins cannot purchase spins'}, status=403)
    key_id, key_secret = get_razorpay_keys()
    if not key_id or not key_secret:
        return JsonResponse({'error': 'Payment gateway not configured. Please contact admin.'}, status=503)
    spin_cfg = get_spin_settings()
    spin_pack_amount = spin_cfg.spin_pack_amount
    spin_pack_spins  = spin_cfg.spin_pack_spins
    try:
        client = razorpay.Client(auth=(key_id, key_secret))
        amount_paise = int(spin_pack_amount * 100)
        order = client.order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'payment_capture': 1,
            'notes': {
                'user_id': str(request.user.id),
                'spins': str(spin_pack_spins),
                'description': f'{spin_pack_spins} Jackpot Spins'
            }
        })
        SpinPurchase.objects.create(
            user=request.user,
            spins_purchased=spin_pack_spins,
            amount=spin_pack_amount,
            razorpay_order_id=order['id'],
            status='pending'
        )
        return JsonResponse({
            'order_id': order['id'],
            'amount':   amount_paise,
            'currency': 'INR',
            'key_id':   key_id,
            'name':     request.user.first_name or request.user.username,
            'email':    request.user.email,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ── Jackpot: Buy Spin Pack with Wallet Balance ─────────────────────────────────
@require_POST
def jackpot_buy_with_wallet(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    if request.user.is_superuser:
        return JsonResponse({'error': 'Admins cannot purchase spins'}, status=403)
    spin_cfg = get_spin_settings()
    spin_pack_amount = spin_cfg.spin_pack_amount
    spin_pack_spins  = spin_cfg.spin_pack_spins
    with transaction.atomic():
        wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
        if wallet.balance < spin_pack_amount:
            return JsonResponse({
                'error': f'Insufficient wallet balance. Please add at least ₹{spin_pack_amount}.',
                'needs_topup': True,
            }, status=402)
        wallet.balance -= spin_pack_amount
        wallet.save()
        WalletTransaction.objects.create(
            wallet=wallet, amount=spin_pack_amount, txn_type='debit',
            description=f'{spin_pack_spins} Jackpot Spins (wallet purchase)',
        )
        SpinPurchase.objects.create(
            user=request.user,
            spins_purchased=spin_pack_spins,
            amount=spin_pack_amount,
            status='success',
        )
        spin_wallet, _ = SpinWallet.objects.select_for_update().get_or_create(user=request.user)
        spin_wallet.spins += spin_pack_spins
        spin_wallet.save()
    return JsonResponse({
        'success':         True,
        'spins_credited':  spin_pack_spins,
        'total_spins':     spin_wallet.spins,
        'new_balance':     float(wallet.balance),
        'message':         f'🎉 {spin_pack_spins} spins credited to your account!'
    })


# ── Jackpot: Verify Payment & Credit Spins ─────────────────────────────────────
@require_POST
def jackpot_verify_payment(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    _, key_secret = get_razorpay_keys()
    if not key_secret:
        return JsonResponse({'success': False, 'error': 'Payment gateway not configured'}, status=503)
    try:
        data = json.loads(request.body)
        razorpay_order_id   = data.get('razorpay_order_id', '')
        razorpay_payment_id = data.get('razorpay_payment_id', '')
        razorpay_signature  = data.get('razorpay_signature', '')
        msg      = f"{razorpay_order_id}|{razorpay_payment_id}"
        expected = hmac.new(key_secret.encode(), msg.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, razorpay_signature):
            return JsonResponse({'success': False, 'error': 'Invalid payment signature'}, status=400)
        with transaction.atomic():
            purchase = SpinPurchase.objects.select_for_update().filter(
                user=request.user, razorpay_order_id=razorpay_order_id, status='pending'
            ).first()
            if not purchase:
                return JsonResponse({'success': False, 'error': 'Purchase record not found'}, status=404)
            purchase.razorpay_payment_id = razorpay_payment_id
            purchase.status = 'success'
            purchase.save()
            spin_wallet, _ = SpinWallet.objects.select_for_update().get_or_create(user=request.user)
            spin_wallet.spins += purchase.spins_purchased
            spin_wallet.save()
        return JsonResponse({
            'success': True,
            'spins_credited': purchase.spins_purchased,
            'total_spins': spin_wallet.spins,
            'message': f'🎉 {purchase.spins_purchased} spins credited to your account!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ── Jackpot: Use a Spin ─────────────────────────────────────────────────────────
@require_POST
def jackpot_use_spin(request):
    """Deducts one spin from the user's spin wallet. Spins are prepaid when the pack
    is purchased via Razorpay, so using one never touches wallet balance.
    No winning logic — every spin is a loss."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required', 'needs_login': True}, status=401)
    with transaction.atomic():
        spin_wallet, _ = SpinWallet.objects.select_for_update().get_or_create(user=request.user)
        if spin_wallet.spins < 1:
            return JsonResponse({'success': False, 'error': 'No spins available. Please buy more spins.', 'needs_topup': True}, status=400)
        spin_wallet.spins -= 1
        spin_wallet.save()
    return JsonResponse({'success': True, 'remaining_spins': spin_wallet.spins})


# ── Jackpot: Claim Win — DISABLED (no winning)
@require_POST
def jackpot_claim_win(request):
    """Winning is disabled. This endpoint always returns no-prize."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    return JsonResponse({'success': False, 'error': 'No prizes available on this machine.'}, status=200)


# ── Coin Flip: Play a Round ─────────────────────────────────────────────────────
@require_POST
def coinflip_play(request):
    """Real win/lose game. Bet is debited immediately; a win credits
    bet_amount * win_multiplier back to the wallet. Outcome is decided
    server-side with a CSPRNG — never trust a client-supplied result."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required', 'needs_login': True}, status=401)
    if request.user.is_superuser:
        return JsonResponse({'error': 'Admins cannot play'}, status=403)

    cfg = get_coinflip_settings()
    if not cfg.is_active:
        return JsonResponse({'error': 'Coin Flip is currently unavailable'}, status=503)

    try:
        data   = json.loads(request.body)
        choice = data.get('choice')
        bet_amount = Decimal(str(data.get('bet_amount', '0')))
    except (ValueError, TypeError, InvalidOperation, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if choice not in ('heads', 'tails'):
        return JsonResponse({'error': 'Choose heads or tails'}, status=400)
    if bet_amount < cfg.min_bet or bet_amount > cfg.max_bet:
        return JsonResponse({'error': f'Bet must be between ₹{cfg.min_bet} and ₹{cfg.max_bet}'}, status=400)

    with transaction.atomic():
        wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
        if wallet.balance < bet_amount:
            return JsonResponse({'error': 'Insufficient wallet balance', 'needs_topup': True}, status=402)

        wallet.balance -= bet_amount
        WalletTransaction.objects.create(
            wallet=wallet, amount=bet_amount, txn_type='debit',
            description='Coin Flip bet',
        )

        result = secrets.choice(['heads', 'tails'])
        won    = (result == choice)
        payout = (bet_amount * cfg.win_multiplier).quantize(Decimal('0.01')) if won else Decimal('0.00')

        if won:
            wallet.balance += payout
            WalletTransaction.objects.create(
                wallet=wallet, amount=payout, txn_type='credit',
                description='Coin Flip payout',
            )
        wallet.save()

        CoinFlipBet.objects.create(
            user=request.user, bet_amount=bet_amount, choice=choice,
            result=result, won=won, payout=payout,
        )

    return JsonResponse({
        'success':     True,
        'result':      result,
        'won':         won,
        'payout':      float(payout),
        'new_balance': float(wallet.balance),
    })


# ── Dice Roll: Play a Round ─────────────────────────────────────────────────────
def _dice_multiplier(win_chance_percent, house_edge_percent):
    """Multiplier derivation shared by the live-preview check and the actual play,
    so the UI's odds display always matches what the server actually pays."""
    return ((Decimal('100') - house_edge_percent) / win_chance_percent).quantize(Decimal('0.01'))


@require_POST
def dice_play(request):
    """Real win/lose game. Roll is 0-99, decided server-side with a CSPRNG.
    Player picks Under/Over and a target (2-97); the payout multiplier is
    derived from win chance & house edge so every target carries the same
    house edge. Bet is debited immediately; a win credits the multiplier
    back to the wallet."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required', 'needs_login': True}, status=401)
    if request.user.is_superuser:
        return JsonResponse({'error': 'Admins cannot play'}, status=403)

    cfg = get_dice_settings()
    if not cfg.is_active:
        return JsonResponse({'error': 'Dice Roll is currently unavailable'}, status=503)

    try:
        data       = json.loads(request.body)
        direction  = data.get('direction')
        target     = int(data.get('target', 0))
        bet_amount = Decimal(str(data.get('bet_amount', '0')))
    except (ValueError, TypeError, InvalidOperation, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if direction not in ('under', 'over'):
        return JsonResponse({'error': 'Choose Roll Under or Roll Over'}, status=400)
    if target < 2 or target > 97:
        return JsonResponse({'error': 'Target must be between 2 and 97'}, status=400)
    if bet_amount < cfg.min_bet or bet_amount > cfg.max_bet:
        return JsonResponse({'error': f'Bet must be between ₹{cfg.min_bet} and ₹{cfg.max_bet}'}, status=400)

    win_chance_percent = Decimal(target) if direction == 'under' else Decimal(99 - target)
    multiplier = _dice_multiplier(win_chance_percent, cfg.house_edge_percent)

    with transaction.atomic():
        wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
        if wallet.balance < bet_amount:
            return JsonResponse({'error': 'Insufficient wallet balance', 'needs_topup': True}, status=402)

        wallet.balance -= bet_amount
        WalletTransaction.objects.create(
            wallet=wallet, amount=bet_amount, txn_type='debit',
            description='Dice Roll bet',
        )

        roll = secrets.randbelow(100)  # 0-99
        won  = (roll < target) if direction == 'under' else (roll > target)
        payout = (bet_amount * multiplier).quantize(Decimal('0.01')) if won else Decimal('0.00')

        if won:
            wallet.balance += payout
            WalletTransaction.objects.create(
                wallet=wallet, amount=payout, txn_type='credit',
                description='Dice Roll payout',
            )
        wallet.save()

        DiceBet.objects.create(
            user=request.user, bet_amount=bet_amount, direction=direction,
            target=target, roll=roll, won=won, multiplier=multiplier, payout=payout,
        )

    return JsonResponse({
        'success':     True,
        'roll':        roll,
        'won':         won,
        'multiplier':  float(multiplier),
        'payout':      float(payout),
        'new_balance': float(wallet.balance),
    })


# ── Card High-Low: Deal & Resolve ───────────────────────────────────────────────
CARD_RANKS = list(range(2, 15))  # 2..14, Ace = 14 (high)
CARD_SUITS = ['S', 'H', 'D', 'C']


def _draw_card():
    return secrets.choice(CARD_RANKS), secrets.choice(CARD_SUITS)


def _hilo_win_chance_percent(rank, choice):
    """Odds are computed against a fresh 51-card remainder (4 of each rank,
    minus the dealt card) — each round is an independent fresh deck, not a
    depleting shoe across rounds."""
    count = 4 * (14 - rank) if choice == 'higher' else 4 * (rank - 2)
    return Decimal(count) / Decimal(51) * Decimal(100)


@require_POST
def cardhilo_deal(request):
    """Phase 1: take the bet, draw & persist the current card server-side.
    The card must live in the DB (not be trusted from the client on resolve)
    or a client could fake a guaranteed-win 'current card' on the next call."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required', 'needs_login': True}, status=401)
    if request.user.is_superuser:
        return JsonResponse({'error': 'Admins cannot play'}, status=403)

    cfg = get_cardhilo_settings()
    if not cfg.is_active:
        return JsonResponse({'error': 'Card High-Low is currently unavailable'}, status=503)

    try:
        data = json.loads(request.body)
        bet_amount = Decimal(str(data.get('bet_amount', '0')))
    except (ValueError, TypeError, InvalidOperation, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if bet_amount < cfg.min_bet or bet_amount > cfg.max_bet:
        return JsonResponse({'error': f'Bet must be between ₹{cfg.min_bet} and ₹{cfg.max_bet}'}, status=400)

    with transaction.atomic():
        if CardHighLowRound.objects.select_for_update().filter(user=request.user, status='dealt').exists():
            return JsonResponse({'error': 'Finish your current round first — choose Higher or Lower.'}, status=409)

        wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
        if wallet.balance < bet_amount:
            return JsonResponse({'error': 'Insufficient wallet balance', 'needs_topup': True}, status=402)

        wallet.balance -= bet_amount
        wallet.save()
        WalletTransaction.objects.create(
            wallet=wallet, amount=bet_amount, txn_type='debit',
            description='Card High-Low bet',
        )

        rank, suit = _draw_card()
        round_obj = CardHighLowRound.objects.create(
            user=request.user, bet_amount=bet_amount,
            current_rank=rank, current_suit=suit,
        )

    return JsonResponse({
        'success':     True,
        'round_id':    round_obj.id,
        'rank':        rank,
        'suit':        suit,
        'can_higher':  rank < 14,
        'can_lower':   rank > 2,
        'new_balance': float(wallet.balance),
    })


@require_POST
def cardhilo_resolve(request):
    """Phase 2: player calls Higher/Lower against the previously dealt card."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required', 'needs_login': True}, status=401)

    cfg = get_cardhilo_settings()

    try:
        data     = json.loads(request.body)
        round_id = int(data.get('round_id', 0))
        choice   = data.get('choice')
    except (ValueError, TypeError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if choice not in ('higher', 'lower'):
        return JsonResponse({'error': 'Choose Higher or Lower'}, status=400)

    with transaction.atomic():
        round_obj = CardHighLowRound.objects.select_for_update().filter(
            id=round_id, user=request.user, status='dealt'
        ).first()
        if not round_obj:
            return JsonResponse({'error': 'Round not found or already resolved'}, status=404)

        if choice == 'higher' and round_obj.current_rank >= 14:
            return JsonResponse({'error': 'Cannot call Higher on an Ace'}, status=400)
        if choice == 'lower' and round_obj.current_rank <= 2:
            return JsonResponse({'error': 'Cannot call Lower on a 2'}, status=400)

        win_chance_percent = _hilo_win_chance_percent(round_obj.current_rank, choice)
        multiplier = _dice_multiplier(win_chance_percent, cfg.house_edge_percent)

        next_rank, next_suit = _draw_card()
        if choice == 'higher':
            won = next_rank > round_obj.current_rank
        else:
            won = next_rank < round_obj.current_rank
        # a tie (next_rank == current_rank) is not a win either way

        payout = (round_obj.bet_amount * multiplier).quantize(Decimal('0.01')) if won else Decimal('0.00')

        wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
        if won:
            wallet.balance += payout
            wallet.save()
            WalletTransaction.objects.create(
                wallet=wallet, amount=payout, txn_type='credit',
                description='Card High-Low payout',
            )

        round_obj.next_rank   = next_rank
        round_obj.next_suit   = next_suit
        round_obj.choice      = choice
        round_obj.status      = 'resolved'
        round_obj.won         = won
        round_obj.multiplier  = multiplier
        round_obj.payout      = payout
        round_obj.resolved_at = timezone.now()
        round_obj.save()

    return JsonResponse({
        'success':     True,
        'next_rank':   next_rank,
        'next_suit':   next_suit,
        'won':         won,
        'multiplier':  float(multiplier),
        'payout':      float(payout),
        'new_balance': float(wallet.balance),
    })


# ── Andar Bahar: Play a Round ───────────────────────────────────────────────────
@require_POST
def andarbahar_play(request):
    """Real win/lose game, ~50/50 side bet — same shape as Coin Flip."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required', 'needs_login': True}, status=401)
    if request.user.is_superuser:
        return JsonResponse({'error': 'Admins cannot play'}, status=403)

    cfg = get_andarbahar_settings()
    if not cfg.is_active:
        return JsonResponse({'error': 'Andar Bahar is currently unavailable'}, status=503)

    try:
        data       = json.loads(request.body)
        choice     = data.get('choice')
        bet_amount = Decimal(str(data.get('bet_amount', '0')))
    except (ValueError, TypeError, InvalidOperation, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if choice not in ('andar', 'bahar'):
        return JsonResponse({'error': 'Choose Andar or Bahar'}, status=400)
    if bet_amount < cfg.min_bet or bet_amount > cfg.max_bet:
        return JsonResponse({'error': f'Bet must be between ₹{cfg.min_bet} and ₹{cfg.max_bet}'}, status=400)

    with transaction.atomic():
        wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
        if wallet.balance < bet_amount:
            return JsonResponse({'error': 'Insufficient wallet balance', 'needs_topup': True}, status=402)

        wallet.balance -= bet_amount
        WalletTransaction.objects.create(
            wallet=wallet, amount=bet_amount, txn_type='debit',
            description='Andar Bahar bet',
        )

        result = secrets.choice(['andar', 'bahar'])
        won    = (result == choice)
        payout = (bet_amount * cfg.win_multiplier).quantize(Decimal('0.01')) if won else Decimal('0.00')

        if won:
            wallet.balance += payout
            WalletTransaction.objects.create(
                wallet=wallet, amount=payout, txn_type='credit',
                description='Andar Bahar payout',
            )
        wallet.save()

        AndarBaharBet.objects.create(
            user=request.user, bet_amount=bet_amount, choice=choice,
            result=result, won=won, payout=payout,
        )

    return JsonResponse({
        'success':     True,
        'result':      result,
        'won':         won,
        'payout':      float(payout),
        'new_balance': float(wallet.balance),
    })


# ── Roulette: Play a Round ──────────────────────────────────────────────────────
ROULETTE_RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}


def _roulette_color(number):
    if number == 0:
        return 'green'
    return 'red' if number in ROULETTE_RED_NUMBERS else 'black'


@require_POST
def roulette_play(request):
    """Real win/lose game. European single-zero wheel (0-36). Bet on a
    color (18/37 true odds) or a single number (1/37 true odds)."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required', 'needs_login': True}, status=401)
    if request.user.is_superuser:
        return JsonResponse({'error': 'Admins cannot play'}, status=403)

    cfg = get_roulette_settings()
    if not cfg.is_active:
        return JsonResponse({'error': 'Roulette is currently unavailable'}, status=503)

    try:
        data       = json.loads(request.body)
        bet_type   = data.get('bet_type')
        bet_value  = str(data.get('bet_value', '')).strip().lower()
        bet_amount = Decimal(str(data.get('bet_amount', '0')))
    except (ValueError, TypeError, InvalidOperation, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if bet_type not in ('color', 'number'):
        return JsonResponse({'error': 'Invalid bet type'}, status=400)
    if bet_type == 'color' and bet_value not in ('red', 'black'):
        return JsonResponse({'error': 'Choose red or black'}, status=400)
    if bet_type == 'number' and (not bet_value.isdigit() or not (0 <= int(bet_value) <= 36)):
        return JsonResponse({'error': 'Number bet must be 0-36'}, status=400)
    if bet_amount < cfg.min_bet or bet_amount > cfg.max_bet:
        return JsonResponse({'error': f'Bet must be between ₹{cfg.min_bet} and ₹{cfg.max_bet}'}, status=400)

    win_chance_percent = Decimal('48.6486486') if bet_type == 'color' else Decimal('2.7027027')
    multiplier = _dice_multiplier(win_chance_percent, cfg.house_edge_percent)

    with transaction.atomic():
        wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
        if wallet.balance < bet_amount:
            return JsonResponse({'error': 'Insufficient wallet balance', 'needs_topup': True}, status=402)

        wallet.balance -= bet_amount
        WalletTransaction.objects.create(
            wallet=wallet, amount=bet_amount, txn_type='debit',
            description='Roulette bet',
        )

        result_number = secrets.randbelow(37)  # 0-36
        result_color  = _roulette_color(result_number)
        won = (bet_value == result_color) if bet_type == 'color' else (int(bet_value) == result_number)

        payout = (bet_amount * multiplier).quantize(Decimal('0.01')) if won else Decimal('0.00')

        if won:
            wallet.balance += payout
            WalletTransaction.objects.create(
                wallet=wallet, amount=payout, txn_type='credit',
                description='Roulette payout',
            )
        wallet.save()

        RouletteBet.objects.create(
            user=request.user, bet_amount=bet_amount, bet_type=bet_type,
            bet_value=bet_value, result_number=result_number, result_color=result_color,
            won=won, multiplier=multiplier, payout=payout,
        )

    return JsonResponse({
        'success':       True,
        'result_number': result_number,
        'result_color':  result_color,
        'won':           won,
        'multiplier':    float(multiplier),
        'payout':        float(payout),
        'new_balance':   float(wallet.balance),
    })


# ── Sic Bo: Play a Round ────────────────────────────────────────────────────────
def _sicbo_roll():
    return secrets.randbelow(6) + 1, secrets.randbelow(6) + 1, secrets.randbelow(6) + 1


@require_POST
def sicbo_play(request):
    """Real win/lose game. 3 dice; bet Big (11-17) or Small (4-10). A
    triple (all 3 dice equal) always loses both sides, matching real
    Sic Bo mechanics — true odds are 105/216 (~48.61%) for each side."""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required', 'needs_login': True}, status=401)
    if request.user.is_superuser:
        return JsonResponse({'error': 'Admins cannot play'}, status=403)

    cfg = get_sicbo_settings()
    if not cfg.is_active:
        return JsonResponse({'error': 'Sic Bo is currently unavailable'}, status=503)

    try:
        data       = json.loads(request.body)
        choice     = data.get('choice')
        bet_amount = Decimal(str(data.get('bet_amount', '0')))
    except (ValueError, TypeError, InvalidOperation, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if choice not in ('big', 'small'):
        return JsonResponse({'error': 'Choose Big or Small'}, status=400)
    if bet_amount < cfg.min_bet or bet_amount > cfg.max_bet:
        return JsonResponse({'error': f'Bet must be between ₹{cfg.min_bet} and ₹{cfg.max_bet}'}, status=400)

    win_chance_percent = Decimal('48.6111')
    multiplier = _dice_multiplier(win_chance_percent, cfg.house_edge_percent)

    with transaction.atomic():
        wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
        if wallet.balance < bet_amount:
            return JsonResponse({'error': 'Insufficient wallet balance', 'needs_topup': True}, status=402)

        wallet.balance -= bet_amount
        WalletTransaction.objects.create(
            wallet=wallet, amount=bet_amount, txn_type='debit',
            description='Sic Bo bet',
        )

        d1, d2, d3 = _sicbo_roll()
        total     = d1 + d2 + d3
        is_triple = (d1 == d2 == d3)

        if is_triple:
            won = False
        elif choice == 'big':
            won = 11 <= total <= 17
        else:
            won = 4 <= total <= 10

        payout = (bet_amount * multiplier).quantize(Decimal('0.01')) if won else Decimal('0.00')

        if won:
            wallet.balance += payout
            WalletTransaction.objects.create(
                wallet=wallet, amount=payout, txn_type='credit',
                description='Sic Bo payout',
            )
        wallet.save()

        SicBoBet.objects.create(
            user=request.user, bet_amount=bet_amount, choice=choice,
            die1=d1, die2=d2, die3=d3, total=total,
            won=won, multiplier=multiplier, payout=payout,
        )

    return JsonResponse({
        'success':     True,
        'die1': d1, 'die2': d2, 'die3': d3, 'total': total,
        'won':         won,
        'multiplier':  float(multiplier),
        'payout':      float(payout),
        'new_balance': float(wallet.balance),
    })
