from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import OperationalError
from django.db.models import Sum
import json, os, hmac, hashlib
from decimal import Decimal

from .models import (
    UserProfile, Wallet, WalletTransaction, Payment,
    SpinWallet, SpinPurchase, RazorpaySettings, SpinMachineSettings
)

# ── Admin credentials (env or hardcoded fallback) ─────────────────────────────
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_EMAIL    = os.environ.get('ADMIN_EMAIL',    'admin@gmail.com')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')


def get_razorpay_keys():
    """Return (key_id, key_secret) from DB singleton, falling back to env vars."""
    try:
        cfg = RazorpaySettings.get_singleton()
        key_id     = cfg.key_id     or os.environ.get('RAZORPAY_KEY_ID', '')
        key_secret = cfg.key_secret or os.environ.get('RAZORPAY_KEY_SECRET', '')
    except Exception:
        key_id     = os.environ.get('RAZORPAY_KEY_ID', '')
        key_secret = os.environ.get('RAZORPAY_KEY_SECRET', '')
    return key_id, key_secret


def get_spin_settings():
    """Returns the SpinMachineSettings singleton. Safe fallback if table missing."""
    try:
        return SpinMachineSettings.get_singleton()
    except Exception:
        class _Fallback:
            spin_pack_spins        = 3
            spin_pack_amount       = Decimal('10.00')
            prize_diamonds         = Decimal('500.00')
            prize_sevens           = Decimal('300.00')
            prize_cherries         = Decimal('100.00')
            prize_two_of_kind      = Decimal('20.00')
            jackpot_display_amount = '84,52,910'
            winning_reel_1         = '7'
            winning_reel_2         = 'X'
            winning_reel_3         = '7'
            is_active              = True
            updated_at             = None
        return _Fallback()


# ── Helpers ───────────────────────────────────────────────────────────────────
def _get_or_create_wallet(user):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet


def _get_or_create_spin_wallet(user):
    sw, _ = SpinWallet.objects.get_or_create(user=user)
    return sw


# ── Home ──────────────────────────────────────────────────────────────────────
def home(request):
    spin_wallet = None
    if request.user.is_authenticated:
        spin_wallet = _get_or_create_spin_wallet(request.user)

    spin_cfg = get_spin_settings()
    return render(request, 'index.html', {
        'spin_wallet':             spin_wallet,
        'spin_pack_amount':        spin_cfg.spin_pack_amount,
        'spin_pack_spins':         spin_cfg.spin_pack_spins,
        'spin_machine_active':     spin_cfg.is_active,
        'jackpot_display_amount':  spin_cfg.jackpot_display_amount,
        'winning_reel_1':          spin_cfg.winning_reel_1,
        'winning_reel_2':          spin_cfg.winning_reel_2,
        'winning_reel_3':          spin_cfg.winning_reel_3,
        'prize_diamonds':          spin_cfg.prize_diamonds,
        'prize_sevens':            spin_cfg.prize_sevens,
        'prize_cherries':          spin_cfg.prize_cherries,
        'prize_two_of_kind':       spin_cfg.prize_two_of_kind,
    })


# ── Auth ──────────────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username     = request.POST.get('username', '').strip()
        first_name   = request.POST.get('first_name', '').strip()
        last_name    = request.POST.get('last_name', '').strip()
        email        = request.POST.get('email', '').strip()
        phone        = request.POST.get('phone_number', '').strip()
        age_str      = request.POST.get('age', '').strip()
        password1    = request.POST.get('password1', '')
        password2    = request.POST.get('password2', '')
        is_above_18  = request.POST.get('is_above_18') == 'on'
        agreed       = request.POST.get('agreed_to_terms') == 'on'

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('signup')
        if UserProfile.objects.filter(phone_number=phone).exists():
            messages.error(request, 'Phone number already registered.')
            return redirect('signup')
        try:
            age = int(age_str) if age_str else None
        except ValueError:
            age = None

        user = User.objects.create_user(
            username=username, email=email, password=password1,
            first_name=first_name, last_name=last_name,
        )
        UserProfile.objects.create(
            user=user, last_name=last_name, age=age,
            phone_number=phone, is_above_18=is_above_18,
            agreed_to_terms=agreed,
        )
        Wallet.objects.create(user=user)
        login(request, user)
        messages.success(request, f'Welcome, {first_name}! Your account is ready.')
        return redirect('home')
    return render(request, 'signup.html')


def logout_view(request):
    logout(request)
    return redirect('home')


# ── Wallet ────────────────────────────────────────────────────────────────────
def add_money_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.is_superuser:
        messages.error(request, 'Admins cannot add money to wallets.')
        return redirect('admin_panel')
    key_id, _ = get_razorpay_keys()
    wallet = _get_or_create_wallet(request.user)
    return render(request, 'add_money.html', {
        'razorpay_key_id': key_id,
        'wallet': wallet,
    })


def my_wallet_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    wallet = _get_or_create_wallet(request.user)
    transactions = wallet.transactions.all()[:50]
    spin_wallet  = _get_or_create_spin_wallet(request.user)
    spin_cfg     = get_spin_settings()
    key_id, _    = get_razorpay_keys()
    return render(request, 'my_wallet.html', {
        'wallet':           wallet,
        'transactions':     transactions,
        'spin_wallet':      spin_wallet,
        'spin_pack_amount': spin_cfg.spin_pack_amount,
        'spin_pack_spins':  spin_cfg.spin_pack_spins,
        'razorpay_key_id':  key_id,
        'prize_diamonds':   spin_cfg.prize_diamonds,
        'prize_sevens':     spin_cfg.prize_sevens,
        'prize_cherries':   spin_cfg.prize_cherries,
        'prize_two_of_kind':spin_cfg.prize_two_of_kind,
        'winning_reel_1':   spin_cfg.winning_reel_1,
        'winning_reel_2':   spin_cfg.winning_reel_2,
        'winning_reel_3':   spin_cfg.winning_reel_3,
    })


@require_POST
def wallet_create_order(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    if request.user.is_superuser:
        return JsonResponse({'error': 'Admins cannot create wallet orders'}, status=403)
    try:
        import razorpay
        key_id, key_secret = get_razorpay_keys()
        if not key_id or not key_secret:
            return JsonResponse({'error': 'Payment gateway not configured. Please contact support.'}, status=400)
        data   = json.loads(request.body)
        amount = int(float(data.get('amount', 0)) * 100)
        if amount < 100:
            return JsonResponse({'error': 'Minimum add amount is ₹1'}, status=400)
        client = razorpay.Client(auth=(key_id, key_secret))
        order  = client.order.create({
            'amount':   amount,
            'currency': 'INR',
            'payment_capture': 1,
            'notes': {'purpose': 'wallet_topup', 'user': request.user.username},
        })
        Payment.objects.create(
            user=request.user,
            amount=amount / 100,
            status='pending',
            transaction_id=order['id'],
            description='Wallet top-up',
        )
        return JsonResponse({'order_id': order['id'], 'amount': amount, 'currency': 'INR', 'key_id': key_id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def wallet_verify_payment(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    try:
        import razorpay
        key_id, key_secret = get_razorpay_keys()
        data       = json.loads(request.body)
        order_id   = data.get('razorpay_order_id')
        payment_id = data.get('razorpay_payment_id')
        signature  = data.get('razorpay_signature')

        generated = hmac.new(key_secret.encode(), f'{order_id}|{payment_id}'.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(generated, signature):
            return JsonResponse({'success': False, 'error': 'Signature mismatch'}, status=400)

        payment = Payment.objects.get(transaction_id=order_id, user=request.user)
        payment.status = 'success'
        payment.razorpay_payment_id = payment_id
        payment.save()

        wallet = _get_or_create_wallet(request.user)
        wallet.balance += payment.amount
        wallet.save()
        WalletTransaction.objects.create(
            wallet=wallet, amount=payment.amount,
            txn_type='credit', description=f'Wallet top-up via Razorpay ({payment_id})',
        )
        return JsonResponse({'success': True, 'new_balance': float(wallet.balance)})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ── Profile ───────────────────────────────────────────────────────────────────
def edit_profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    profile = getattr(request.user, 'profile', None)
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.email      = request.POST.get('email', '').strip()
        request.user.save()
        if profile:
            profile.phone_number = request.POST.get('phone_number', profile.phone_number).strip()
            age_str = request.POST.get('age', '').strip()
            profile.age = int(age_str) if age_str.isdigit() else profile.age
            profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('edit_profile')
    return render(request, 'edit_profile.html', {'profile': profile})


def change_password_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        old_pw  = request.POST.get('old_password', '')
        new_pw1 = request.POST.get('new_password1', '')
        new_pw2 = request.POST.get('new_password2', '')
        if not request.user.check_password(old_pw):
            messages.error(request, 'Current password is incorrect.')
            return redirect('change_password')
        if new_pw1 != new_pw2:
            messages.error(request, 'New passwords do not match.')
            return redirect('change_password')
        if len(new_pw1) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return redirect('change_password')
        request.user.set_password(new_pw1)
        request.user.save()
        login(request, request.user)
        messages.success(request, 'Password changed successfully.')
        return redirect('change_password')
    return render(request, 'change_password.html')


# ── Admin Panel ───────────────────────────────────────────────────────────────
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
        spin_purchases        = SpinPurchase.objects.select_related('user').order_by('-created_at')
        spin_total_revenue    = spin_purchases.filter(status='success').aggregate(s=Sum('amount'))['s'] or 0
        spin_total_spins_sold = spin_purchases.filter(status='success').aggregate(s=Sum('spins_purchased'))['s'] or 0
        spin_unique_buyers    = spin_purchases.filter(status='success').values('user').distinct().count()
        spin_purchases_count  = spin_purchases.filter(status='success').count()
        spin_recent           = list(spin_purchases[:10])
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


# ── Admin: Save Razorpay Settings ─────────────────────────────────────────────
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


# ── Admin: Save Spin Machine Settings ────────────────────────────────────────
@require_POST
def save_spin_settings(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('login')
    try:
        cfg = SpinMachineSettings.get_singleton()
        cfg.spin_pack_spins           = int(request.POST.get('spin_pack_spins', 3))
        cfg.spin_pack_amount          = Decimal(request.POST.get('spin_pack_amount', '10.00'))
        cfg.prize_diamonds            = Decimal(request.POST.get('prize_diamonds', '500.00'))
        cfg.prize_sevens              = Decimal(request.POST.get('prize_sevens', '300.00'))
        cfg.prize_cherries            = Decimal(request.POST.get('prize_cherries', '100.00'))
        cfg.prize_two_of_kind         = Decimal(request.POST.get('prize_two_of_kind', '20.00'))
        cfg.jackpot_display_amount    = request.POST.get('jackpot_display_amount', '84,52,910').strip()
        cfg.winning_reel_1            = request.POST.get('winning_reel_1', '7').strip() or '7'
        cfg.winning_reel_2            = request.POST.get('winning_reel_2', 'X').strip() or 'X'
        cfg.winning_reel_3            = request.POST.get('winning_reel_3', '7').strip() or '7'
        cfg.is_active                 = request.POST.get('is_active') == 'on'
        if cfg.spin_pack_spins < 1:
            raise ValueError('Spins per pack must be at least 1')
        if cfg.spin_pack_amount <= 0:
            raise ValueError('Pack price must be greater than ₹0')
        cfg.save()
        messages.success(request, '✅ Spin machine settings saved! Frontend is now live with new values.')
    except Exception as e:
        messages.error(request, f'Error saving spin settings: {e}')
    return redirect('admin_panel')


# ── Admin: Toggle User Active ─────────────────────────────────────────────────
def toggle_user_active(request, user_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('login')
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    user.is_active = not user.is_active
    user.save()
    status = 'activated' if user.is_active else 'banned'
    messages.success(request, f'User @{user.username} has been {status}.')
    return redirect('admin_panel')


# ── Admin: Delete User ────────────────────────────────────────────────────────
def delete_user(request, user_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('login')
    user = get_object_or_404(User, id=user_id, is_superuser=False)
    username = user.username
    user.delete()
    messages.success(request, f'User @{username} deleted successfully.')
    return redirect('admin_panel')


# ── Admin: Add User ───────────────────────────────────────────────────────────
def admin_add_user(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('login')
    if request.method == 'POST':
        username   = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip()
        phone      = request.POST.get('phone_number', '').strip()
        password   = request.POST.get('password', '')

        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username @{username} already exists.')
            return redirect('admin_panel')
        if phone and UserProfile.objects.filter(phone_number=phone).exists():
            messages.error(request, f'Phone {phone} already registered.')
            return redirect('admin_panel')

        user = User.objects.create_user(
            username=username, email=email, password=password,
            first_name=first_name, last_name=last_name,
        )
        if phone:
            UserProfile.objects.create(user=user, phone_number=phone)
        Wallet.objects.create(user=user)
        messages.success(request, f'User @{username} created successfully.')
    return redirect('admin_panel')


# ── Admin Info ────────────────────────────────────────────────────────────────
def admin_info_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login')
    return render(request, 'admin_info.html', {
        'admin_username': ADMIN_USERNAME,
        'admin_email':    ADMIN_EMAIL,
        'admin_password': ADMIN_PASSWORD,
    })


# ── Jackpot: Create Razorpay Order for Spin Pack ──────────────────────────────
@require_POST
def jackpot_create_order(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    if request.user.is_superuser:
        return JsonResponse({'error': 'Admins cannot purchase spins'}, status=403)

    try:
        import razorpay
        key_id, key_secret = get_razorpay_keys()
        if not key_id or not key_secret:
            return JsonResponse({'error': 'Payment gateway not configured.'}, status=400)

        spin_cfg         = get_spin_settings()
        spin_pack_spins  = spin_cfg.spin_pack_spins
        spin_pack_amount = int(spin_cfg.spin_pack_amount)

        client       = razorpay.Client(auth=(key_id, key_secret))
        amount_paise = int(spin_pack_amount * 100)
        order = client.order.create({
            'amount':   amount_paise,
            'currency': 'INR',
            'payment_capture': 1,
            'notes': {
                'purpose':     'jackpot_spins',
                'user':        request.user.username,
                'spins':       str(spin_pack_spins),
                'description': f'{spin_pack_spins} Jackpot Spins'
            }
        })
        SpinPurchase.objects.create(
            user=request.user,
            spins_purchased=spin_pack_spins,
            amount=spin_pack_amount,
            razorpay_order_id=order['id'],
            status='pending',
        )
        return JsonResponse({
            'order_id': order['id'],
            'amount':   amount_paise,
            'currency': 'INR',
            'key_id':   key_id,
            'spins':    spin_pack_spins,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ── Jackpot: Verify Payment & Credit Spins ────────────────────────────────────
@require_POST
def jackpot_verify_payment(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    try:
        _, key_secret = get_razorpay_keys()
        data       = json.loads(request.body)
        order_id   = data.get('razorpay_order_id')
        payment_id = data.get('razorpay_payment_id')
        signature  = data.get('razorpay_signature')

        generated = hmac.new(key_secret.encode(), f'{order_id}|{payment_id}'.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(generated, signature):
            return JsonResponse({'success': False, 'error': 'Signature mismatch'}, status=400)

        purchase = SpinPurchase.objects.get(razorpay_order_id=order_id, user=request.user)
        purchase.status = 'success'
        purchase.razorpay_payment_id = payment_id
        purchase.save()

        spin_wallet = _get_or_create_spin_wallet(request.user)
        spin_wallet.spins += purchase.spins_purchased
        spin_wallet.save()
        return JsonResponse({
            'success':        True,
            'spins_credited': purchase.spins_purchased,
            'total_spins':    spin_wallet.spins,
            'message':        f'🎉 {purchase.spins_purchased} spins credited to your account!'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ── Jackpot: Use a Spin ───────────────────────────────────────────────────────
@require_POST
def jackpot_use_spin(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    spin_wallet = _get_or_create_spin_wallet(request.user)
    if spin_wallet.spins < 1:
        return JsonResponse({'success': False, 'error': 'No spins available'}, status=400)
    spin_wallet.spins -= 1
    spin_wallet.save()
    return JsonResponse({'success': True, 'remaining_spins': spin_wallet.spins})


# ── Jackpot: Claim Win (credit wallet prize) ──────────────────────────────────
@require_POST
def jackpot_claim_win(request):
    """
    Called by the frontend after a winning spin is confirmed.
    combo: 'diamonds' | 'sevens' | 'cherries' | 'two_of_kind'
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    try:
        data  = json.loads(request.body)
        combo = data.get('combo', '')
        spin_cfg = get_spin_settings()
        prize_map = {
            'diamonds':    spin_cfg.prize_diamonds,
            'sevens':      spin_cfg.prize_sevens,
            'cherries':    spin_cfg.prize_cherries,
            'two_of_kind': spin_cfg.prize_two_of_kind,
        }
        prize = prize_map.get(combo)
        if prize is None or prize <= 0:
            return JsonResponse({'success': False, 'error': 'No prize for this combo'}, status=400)
        wallet = _get_or_create_wallet(request.user)
        wallet.balance += prize
        wallet.save()
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=prize,
            txn_type='credit',
            description=f'Jackpot win — {combo.replace("_", " ").title()} combo!',
        )
        return JsonResponse({
            'success':     True,
            'prize':       float(prize),
            'new_balance': float(wallet.balance),
            'message':     f'🎉 ₹{prize} credited to your wallet!',
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ── JsonResponse import fix ───────────────────────────────────────────────────
from django.http import JsonResponse
