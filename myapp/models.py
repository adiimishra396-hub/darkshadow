from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    last_name = models.CharField(max_length=100, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True)
    is_above_18 = models.BooleanField(default=False)
    agreed_to_terms = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Profile"


class Wallet(models.Model):
    user    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — ₹{self.balance}"


class WalletTransaction(models.Model):
    TYPE_CHOICES = [
        ('credit', 'Credit'),
        ('debit',  'Debit'),
    ]
    wallet      = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount      = models.DecimalField(max_digits=12, decimal_places=2)
    txn_type    = models.CharField(max_length=6, choices=TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.wallet.user.username} | {self.txn_type} | ₹{self.amount}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('success',  'Success'),
        ('failed',   'Failed'),
        ('refunded', 'Refunded'),
    ]
    METHOD_CHOICES = [
        ('upi',        'UPI'),
        ('card',       'Card'),
        ('netbanking', 'Net Banking'),
        ('wallet',     'Wallet'),
        ('other',      'Other'),
    ]
    user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount         = models.DecimalField(max_digits=12, decimal_places=2)
    status         = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    method         = models.CharField(max_length=15, choices=METHOD_CHOICES, default='upi')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    description    = models.CharField(max_length=255, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} | ₹{self.amount} | {self.status}"


class SpinWallet(models.Model):
    """Tracks how many spins a user has available to play."""
    user   = models.OneToOneField(User, on_delete=models.CASCADE, related_name='spin_wallet')
    spins  = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} — {self.spins} spins"


class SpinPurchase(models.Model):
    """Records every spin purchase & Razorpay payment reference."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed',  'Failed'),
    ]
    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name='spin_purchases')
    spins_purchased = models.PositiveIntegerField(default=3)
    amount          = models.DecimalField(max_digits=8, decimal_places=2, default=10.00)
    razorpay_order_id   = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    status          = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} | {self.spins_purchased} spins | {self.status}"


class RazorpaySettings(models.Model):
    """
    Singleton model — always only one row (id=1).
    Admin can update Key ID and Key Secret from the admin panel.
    Falls back to environment variables if the row is empty.
    """
    key_id     = models.CharField(max_length=200, blank=True, default='',
                                  verbose_name='Razorpay Key ID')
    key_secret = models.CharField(max_length=200, blank=True, default='',
                                  verbose_name='Razorpay Key Secret')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Razorpay Settings'

    def __str__(self):
        return f'Razorpay Settings (updated {self.updated_at})'

    @classmethod
    def get_singleton(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SpinMachineSettings(models.Model):
    """
    Singleton model (id=1). Admin sets pricing and prize amounts here.
    All values are picked up dynamically by the home view and jackpot views.
    """
    spin_pack_spins   = models.PositiveIntegerField(default=3,
        help_text='Number of spins per purchase pack')
    spin_pack_amount  = models.DecimalField(max_digits=8, decimal_places=2, default='10.00',
        help_text='Price per spin pack (INR)')
    # Win prize amounts (credited to wallet)
    prize_diamonds    = models.DecimalField(max_digits=10, decimal_places=2, default='500.00',
        help_text='Prize for 3x Diamonds (wallet credit)')
    prize_sevens      = models.DecimalField(max_digits=10, decimal_places=2, default='300.00',
        help_text='Prize for 3x Lucky Sevens (wallet credit)')
    prize_cherries    = models.DecimalField(max_digits=10, decimal_places=2, default='100.00',
        help_text='Prize for 3x Cherries (wallet credit)')
    prize_two_of_kind = models.DecimalField(max_digits=10, decimal_places=2, default='20.00',
        help_text='Prize for any two-of-a-kind match (wallet credit)')
    is_active         = models.BooleanField(default=True,
        help_text='Show/hide the spin machine on the homepage')
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Spin Machine Settings'

    def __str__(self):
        return f'Spin Machine Settings (updated {self.updated_at})'

    @classmethod
    def get_singleton(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
