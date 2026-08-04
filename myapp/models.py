from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


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


class CoinFlipSettings(models.Model):
    """
    Singleton model (id=1). Admin sets Coin Flip odds & bet limits here.
    Real win/lose game — a win pays out bet_amount * win_multiplier.
    """
    win_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.90'),
        help_text='Payout multiplier on a win (e.g. 1.90 = 1.9x the bet back, ~5% house edge)')
    min_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'),
        help_text='Minimum bet amount (INR)')
    max_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5000.00'),
        help_text='Maximum bet amount (INR)')
    is_active  = models.BooleanField(default=True,
        help_text='Show/hide Coin Flip on the homepage')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Coin Flip Settings'
        verbose_name_plural = 'Coin Flip Settings'

    def __str__(self):
        return f'Coin Flip Settings (updated {self.updated_at})'

    @classmethod
    def get_singleton(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class CoinFlipBet(models.Model):
    """Records every Coin Flip play (audit trail for a real win/lose game)."""
    CHOICE_CHOICES = [
        ('heads', 'Heads'),
        ('tails', 'Tails'),
    ]
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coinflip_bets')
    bet_amount = models.DecimalField(max_digits=10, decimal_places=2)
    choice     = models.CharField(max_length=5, choices=CHOICE_CHOICES)
    result     = models.CharField(max_length=5, choices=CHOICE_CHOICES)
    won        = models.BooleanField(default=False)
    payout     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        outcome = 'WON' if self.won else 'LOST'
        return f"{self.user.username} | ₹{self.bet_amount} | called {self.choice}, got {self.result} | {outcome}"


class DiceSettings(models.Model):
    """
    Singleton model (id=1). Admin sets Dice Roll house edge & bet limits.
    Real win/lose game — roll is 0-99. Player picks a target (2-97) and
    Under/Over; payout multiplier is derived from win chance & house edge
    so every target/direction combo carries the same house edge.
    """
    house_edge_percent = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('5.00'),
        help_text='House edge as a percentage (e.g. 5.00 = 5%). Lower = better payouts for players.')
    min_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'),
        help_text='Minimum bet amount (INR)')
    max_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5000.00'),
        help_text='Maximum bet amount (INR)')
    is_active  = models.BooleanField(default=True,
        help_text='Show/hide Dice Roll on the homepage')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dice Roll Settings'
        verbose_name_plural = 'Dice Roll Settings'

    def __str__(self):
        return f'Dice Roll Settings (updated {self.updated_at})'

    @classmethod
    def get_singleton(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class DiceBet(models.Model):
    """Records every Dice Roll play (audit trail for a real win/lose game)."""
    DIRECTION_CHOICES = [
        ('under', 'Roll Under'),
        ('over',  'Roll Over'),
    ]
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dice_bets')
    bet_amount  = models.DecimalField(max_digits=10, decimal_places=2)
    direction   = models.CharField(max_length=5, choices=DIRECTION_CHOICES)
    target      = models.PositiveSmallIntegerField(help_text='Target number (2-97) chosen by the player')
    roll        = models.PositiveSmallIntegerField(help_text='Actual roll, 0-99')
    won         = models.BooleanField(default=False)
    multiplier  = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    payout      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        outcome = 'WON' if self.won else 'LOST'
        return f"{self.user.username} | ₹{self.bet_amount} | {self.direction} {self.target}, rolled {self.roll} | {outcome}"


class CardHighLowSettings(models.Model):
    """
    Singleton model (id=1). Admin sets Card High-Low house edge & bet limits.
    Real win/lose game — a card is dealt, the player calls whether the next
    card will be Higher or Lower; payout multiplier is derived from the
    actual card-count odds for the dealt rank & house edge.
    """
    house_edge_percent = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('5.00'),
        help_text='House edge as a percentage (e.g. 5.00 = 5%). Lower = better payouts for players.')
    min_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'),
        help_text='Minimum bet amount (INR)')
    max_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5000.00'),
        help_text='Maximum bet amount (INR)')
    is_active  = models.BooleanField(default=True,
        help_text='Show/hide Card High-Low on the homepage')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Card High-Low Settings'
        verbose_name_plural = 'Card High-Low Settings'

    def __str__(self):
        return f'Card High-Low Settings (updated {self.updated_at})'

    @classmethod
    def get_singleton(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class CardHighLowRound(models.Model):
    """
    Records every Card High-Low round. Two-phase: a round is created as
    'dealt' when the current card is drawn & the bet is taken, then becomes
    'resolved' once the player calls Higher/Lower and the next card is drawn.
    Server-side state is required here (unlike Coin Flip/Dice) because the
    player must see the dealt card before choosing — trusting a client-sent
    "current card" would let a client fake a guaranteed win.
    """
    CHOICE_CHOICES = [
        ('higher', 'Higher'),
        ('lower',  'Lower'),
    ]
    STATUS_CHOICES = [
        ('dealt',    'Dealt'),
        ('resolved', 'Resolved'),
    ]
    SUIT_CHOICES = [
        ('S', 'Spades'),
        ('H', 'Hearts'),
        ('D', 'Diamonds'),
        ('C', 'Clubs'),
    ]

    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cardhilo_rounds')
    bet_amount   = models.DecimalField(max_digits=10, decimal_places=2)
    current_rank = models.PositiveSmallIntegerField(help_text='2-14 (Ace = 14)')
    current_suit = models.CharField(max_length=1, choices=SUIT_CHOICES)
    next_rank    = models.PositiveSmallIntegerField(null=True, blank=True)
    next_suit    = models.CharField(max_length=1, choices=SUIT_CHOICES, blank=True)
    choice       = models.CharField(max_length=6, choices=CHOICE_CHOICES, blank=True)
    status       = models.CharField(max_length=8, choices=STATUS_CHOICES, default='dealt')
    won          = models.BooleanField(null=True)
    multiplier   = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    payout       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
    resolved_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.status == 'dealt':
            return f"{self.user.username} | ₹{self.bet_amount} | dealt {self.current_rank}{self.current_suit} | awaiting call"
        outcome = 'WON' if self.won else 'LOST'
        return f"{self.user.username} | ₹{self.bet_amount} | {self.current_rank}{self.current_suit} → called {self.choice}, got {self.next_rank}{self.next_suit} | {outcome}"


class AndarBaharSettings(models.Model):
    """Singleton model (id=1). Real win/lose game — near-50/50 side bet."""
    win_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.90'),
        help_text='Payout multiplier on a win (e.g. 1.90 = 1.9x the bet back, ~5% house edge)')
    min_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'))
    max_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5000.00'))
    is_active  = models.BooleanField(default=True, help_text='Show/hide Andar Bahar on the homepage')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Andar Bahar Settings'
        verbose_name_plural = 'Andar Bahar Settings'

    def __str__(self):
        return f'Andar Bahar Settings (updated {self.updated_at})'

    @classmethod
    def get_singleton(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class AndarBaharBet(models.Model):
    """Records every Andar Bahar play."""
    CHOICE_CHOICES = [('andar', 'Andar'), ('bahar', 'Bahar')]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='andarbahar_bets')
    bet_amount = models.DecimalField(max_digits=10, decimal_places=2)
    choice     = models.CharField(max_length=5, choices=CHOICE_CHOICES)
    result     = models.CharField(max_length=5, choices=CHOICE_CHOICES)
    won        = models.BooleanField(default=False)
    payout     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        outcome = 'WON' if self.won else 'LOST'
        return f"{self.user.username} | ₹{self.bet_amount} | called {self.choice}, got {self.result} | {outcome}"


class RouletteSettings(models.Model):
    """
    Singleton model (id=1). European single-zero wheel (0-36). Payout
    multiplier is derived from the true wheel odds for the chosen bet
    type & house edge, same formula family as Dice Roll.
    """
    house_edge_percent = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('5.00'),
        help_text='House edge as a percentage (e.g. 5.00 = 5%). Lower = better payouts for players.')
    min_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'))
    max_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5000.00'))
    is_active  = models.BooleanField(default=True, help_text='Show/hide Roulette on the homepage')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Roulette Settings'
        verbose_name_plural = 'Roulette Settings'

    def __str__(self):
        return f'Roulette Settings (updated {self.updated_at})'

    @classmethod
    def get_singleton(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class RouletteBet(models.Model):
    """Records every Roulette play. bet_type is 'color' or 'number'."""
    BET_TYPE_CHOICES = [('color', 'Color'), ('number', 'Number')]

    user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roulette_bets')
    bet_amount     = models.DecimalField(max_digits=10, decimal_places=2)
    bet_type       = models.CharField(max_length=6, choices=BET_TYPE_CHOICES)
    bet_value      = models.CharField(max_length=10, help_text="'red'/'black' for color bets, '0'-'36' for number bets")
    result_number  = models.PositiveSmallIntegerField(help_text='0-36')
    result_color   = models.CharField(max_length=5, help_text="'red', 'black', or 'green' (for 0)")
    won            = models.BooleanField(default=False)
    multiplier     = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    payout         = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        outcome = 'WON' if self.won else 'LOST'
        return f"{self.user.username} | ₹{self.bet_amount} | {self.bet_type}:{self.bet_value} vs {self.result_number}({self.result_color}) | {outcome}"


class SicBoSettings(models.Model):
    """Singleton model (id=1). Real win/lose game — 3 dice, Big/Small bet."""
    house_edge_percent = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('5.00'),
        help_text='House edge as a percentage on top of true Big/Small odds (~48.6% each).')
    min_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'))
    max_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5000.00'))
    is_active  = models.BooleanField(default=True, help_text='Show/hide Sic Bo on the homepage')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sic Bo Settings'
        verbose_name_plural = 'Sic Bo Settings'

    def __str__(self):
        return f'Sic Bo Settings (updated {self.updated_at})'

    @classmethod
    def get_singleton(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SicBoBet(models.Model):
    """Records every Sic Bo play. A triple (all 3 dice equal) loses both
    Big and Small bets, matching real Sic Bo house-edge mechanics."""
    CHOICE_CHOICES = [('big', 'Big'), ('small', 'Small')]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sicbo_bets')
    bet_amount = models.DecimalField(max_digits=10, decimal_places=2)
    choice     = models.CharField(max_length=5, choices=CHOICE_CHOICES)
    die1       = models.PositiveSmallIntegerField()
    die2       = models.PositiveSmallIntegerField()
    die3       = models.PositiveSmallIntegerField()
    total      = models.PositiveSmallIntegerField()
    won        = models.BooleanField(default=False)
    multiplier = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    payout     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        outcome = 'WON' if self.won else 'LOST'
        return f"{self.user.username} | ₹{self.bet_amount} | called {self.choice}, rolled {self.die1}-{self.die2}-{self.die3}={self.total} | {outcome}"


class TeenPattiSettings(models.Model):
    """
    Singleton model (id=1). Real win/lose game — the player's 3-card hand
    is dealt against a virtual dealer's 3-card hand from a single shuffled
    deck (so hands never share a card) and compared with standard Teen
    Patti hand rankings. A tie is a push — bet refunded, not a loss.
    """
    win_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.90'),
        help_text='Payout multiplier on a win (e.g. 1.90 = 1.9x the bet back)')
    min_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'))
    max_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5000.00'))
    is_active  = models.BooleanField(default=True, help_text='Show/hide Teen Patti on the homepage')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Teen Patti Settings'
        verbose_name_plural = 'Teen Patti Settings'

    def __str__(self):
        return f'Teen Patti Settings (updated {self.updated_at})'

    @classmethod
    def get_singleton(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class TeenPattiBet(models.Model):
    """Records every Teen Patti play — player's 3-card hand vs a virtual
    dealer's 3-card hand, dealt from a single shuffled deck."""
    OUTCOME_CHOICES = [
        ('win',  'Win'),
        ('lose', 'Lose'),
        ('push', 'Push'),
    ]
    user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teenpatti_bets')
    bet_amount       = models.DecimalField(max_digits=10, decimal_places=2)
    player_cards     = models.JSONField(help_text='[[rank, suit], ...] x3')
    dealer_cards     = models.JSONField(help_text='[[rank, suit], ...] x3')
    player_hand_type = models.CharField(max_length=20)
    dealer_hand_type = models.CharField(max_length=20)
    outcome          = models.CharField(max_length=4, choices=OUTCOME_CHOICES)
    payout           = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} | ₹{self.bet_amount} | {self.player_hand_type} vs {self.dealer_hand_type} | {self.outcome.upper()}"


class BlackjackSettings(models.Model):
    """
    Singleton model (id=1). Real win/lose game — standard single-player
    Blackjack vs a virtual dealer (dealer stands on all 17s). Natural
    blackjack (2-card 21) pays blackjack_multiplier; a standard win pays
    win_multiplier; equal totals push (bet refunded).
    """
    win_multiplier       = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.90'),
        help_text='Payout multiplier on a standard win (e.g. 1.90 = 1.9x the bet back)')
    blackjack_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('2.35'),
        help_text='Payout multiplier on a natural blackjack (2-card 21), standard is 3:2')
    min_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'))
    max_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5000.00'))
    is_active  = models.BooleanField(default=True, help_text='Show/hide Blackjack on the homepage')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Blackjack Settings'
        verbose_name_plural = 'Blackjack Settings'

    def __str__(self):
        return f'Blackjack Settings (updated {self.updated_at})'

    @classmethod
    def get_singleton(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class BlackjackRound(models.Model):
    """
    Records every Blackjack round. Two-phase like Card High-Low, but the
    player can Hit an arbitrary number of times before Standing. The
    remaining shuffled deck is persisted server-side (deck field) so hit
    requests keep drawing from the SAME deck across separate HTTP calls
    without risking duplicate cards.
    """
    STATUS_CHOICES = [
        ('active',   'Active'),
        ('resolved', 'Resolved'),
    ]
    OUTCOME_CHOICES = [
        ('win',            'Win'),
        ('blackjack_win',  'Blackjack Win'),
        ('lose',           'Lose'),
        ('push',           'Push'),
    ]
    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blackjack_rounds')
    bet_amount   = models.DecimalField(max_digits=10, decimal_places=2)
    deck         = models.JSONField(help_text='Remaining shuffled deck: [[rank, suit], ...]')
    player_cards = models.JSONField()
    dealer_cards = models.JSONField()
    status       = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    outcome      = models.CharField(max_length=13, choices=OUTCOME_CHOICES, blank=True)
    payout       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
    resolved_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.status == 'active':
            return f"{self.user.username} | ₹{self.bet_amount} | hand in progress"
        return f"{self.user.username} | ₹{self.bet_amount} | {self.outcome.upper()}"


class BaccaratSettings(models.Model):
    """
    Singleton model (id=1). Real win/lose game — Player vs Banker with
    standard baccarat third-card drawing rules (automatic, no player
    decision). Bet on Player, Banker, or Tie. A tie result pushes
    (refunds) Player/Banker bets rather than losing them, matching real
    baccarat rules.
    """
    player_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.90'),
        help_text='Payout multiplier when betting Player and Player wins')
    banker_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.80'),
        help_text='Payout multiplier when betting Banker and Banker wins (lower than Player — Banker wins slightly more often, mirrors the real-world commission)')
    tie_multiplier     = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('9.00'),
        help_text='Payout multiplier when betting Tie and the hand ties (~9-10% chance, standard odds are "8 to 1" i.e. 9x total return)')
    min_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'))
    max_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5000.00'))
    is_active  = models.BooleanField(default=True, help_text='Show/hide Baccarat on the homepage')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Baccarat Settings'
        verbose_name_plural = 'Baccarat Settings'

    def __str__(self):
        return f'Baccarat Settings (updated {self.updated_at})'

    @classmethod
    def get_singleton(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class BaccaratBet(models.Model):
    """Records every Baccarat play."""
    SIDE_CHOICES = [
        ('player', 'Player'),
        ('banker', 'Banker'),
        ('tie',    'Tie'),
    ]
    OUTCOME_CHOICES = [
        ('win',  'Win'),
        ('lose', 'Lose'),
        ('push', 'Push'),
    ]
    user          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='baccarat_bets')
    bet_amount    = models.DecimalField(max_digits=10, decimal_places=2)
    bet_side      = models.CharField(max_length=6, choices=SIDE_CHOICES)
    player_cards  = models.JSONField()
    banker_cards  = models.JSONField()
    player_total  = models.PositiveSmallIntegerField(help_text='0-9')
    banker_total  = models.PositiveSmallIntegerField(help_text='0-9')
    winner        = models.CharField(max_length=6, choices=SIDE_CHOICES)
    outcome       = models.CharField(max_length=4, choices=OUTCOME_CHOICES)
    payout        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} | ₹{self.bet_amount} | bet {self.bet_side}, {self.player_total} vs {self.banker_total} ({self.winner}) | {self.outcome.upper()}"


class PokerSettings(models.Model):
    """
    Singleton model (id=1). Real win/lose game — a simplified single-
    player poker: the player's 5-card hand is dealt against a virtual
    dealer's 5-card hand from a single shuffled deck (so hands never
    share a card) and compared with standard poker hand rankings. This
    is NOT real Texas Hold'em (no community cards or betting rounds) —
    an honest simplification, same spirit as Teen Patti's vs-dealer
    model. A tie is a push — bet refunded.
    """
    win_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.90'),
        help_text='Payout multiplier on a win (e.g. 1.90 = 1.9x the bet back)')
    min_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'))
    max_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5000.00'))
    is_active  = models.BooleanField(default=True, help_text='Show/hide Poker on the homepage')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Poker Settings'
        verbose_name_plural = 'Poker Settings'

    def __str__(self):
        return f'Poker Settings (updated {self.updated_at})'

    @classmethod
    def get_singleton(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class PokerBet(models.Model):
    """Records every Poker play — player's 5-card hand vs a virtual
    dealer's 5-card hand, dealt from a single shuffled deck."""
    OUTCOME_CHOICES = [
        ('win',  'Win'),
        ('lose', 'Lose'),
        ('push', 'Push'),
    ]
    user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poker_bets')
    bet_amount       = models.DecimalField(max_digits=10, decimal_places=2)
    player_cards     = models.JSONField(help_text='[[rank, suit], ...] x5')
    dealer_cards     = models.JSONField(help_text='[[rank, suit], ...] x5')
    player_hand_type = models.CharField(max_length=20)
    dealer_hand_type = models.CharField(max_length=20)
    outcome          = models.CharField(max_length=4, choices=OUTCOME_CHOICES)
    payout           = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} | ₹{self.bet_amount} | {self.player_hand_type} vs {self.dealer_hand_type} | {self.outcome.upper()}"


class RummySettings(models.Model):
    """
    Singleton model (id=1). Real win/lose game — a simplified instant
    Rummy: real Rummy needs multi-turn draw/discard against opponents,
    which doesn't reduce to an instant bet, so this deals a 9-card hand
    and finds the best possible split into three 3-card groups, each
    either a valid Set (3 same rank, distinct suits) or a valid Run (3
    consecutive same-suit ranks, A-2-3 low only). Payout scales with
    how many of the 3 groups are valid. Multiplier defaults are
    calibrated from simulation: ~29.8% of hands get exactly 1 valid
    group, ~1.4% get 2, and 3 valid groups is a near-unicorn event.
    """
    one_group_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.50'),
        help_text='Payout when the best split has exactly 1 valid group (~30% of hands)')
    two_group_multiplier = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('35.00'),
        help_text='Payout when the best split has exactly 2 valid groups (~1.4% of hands)')
    perfect_multiplier    = models.DecimalField(max_digits=7, decimal_places=2, default=Decimal('100.00'),
        help_text='Payout when all 3 groups are valid — extremely rare (not observed in 20,000 simulated hands)')
    min_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'))
    max_bet    = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5000.00'))
    is_active  = models.BooleanField(default=True, help_text='Show/hide Rummy on the homepage')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rummy Settings'
        verbose_name_plural = 'Rummy Settings'

    def __str__(self):
        return f'Rummy Settings (updated {self.updated_at})'

    @classmethod
    def get_singleton(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class RummyBet(models.Model):
    """Records every Rummy play."""
    OUTCOME_CHOICES = [
        ('win',  'Win'),
        ('lose', 'Lose'),
    ]
    user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rummy_bets')
    bet_amount       = models.DecimalField(max_digits=10, decimal_places=2)
    cards            = models.JSONField(help_text='[[rank, suit], ...] x9')
    valid_group_count = models.PositiveSmallIntegerField(help_text='0-3')
    outcome          = models.CharField(max_length=4, choices=OUTCOME_CHOICES)
    multiplier       = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    payout           = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} | ₹{self.bet_amount} | {self.valid_group_count}/3 valid groups | {self.outcome.upper()}"


class SpinMachineSettings(models.Model):
    """
    Singleton model (id=1). Admin sets spin pack pricing and the jackpot
    display amount shown on the homepage here.
    No winning is possible — the spin is purely pay-to-play entertainment.
    """
    spin_pack_spins   = models.PositiveIntegerField(default=3,
        help_text='Number of spins per purchase pack')
    spin_pack_amount  = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('10.00'),
        help_text='Price per spin pack (INR)')
    homepage_jackpot_display = models.CharField(
        max_length=50, default='84,52,910',
        help_text='Jackpot prize amount shown on homepage (e.g. 84,52,910 — no ₹ symbol needed)')
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
