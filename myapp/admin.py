from django import forms
from django.contrib import admin
from .models import (
    UserProfile, Wallet, WalletTransaction, Payment,
    SpinWallet, SpinPurchase, RazorpaySettings, SpinMachineSettings,
    CoinFlipSettings, CoinFlipBet, DiceSettings, DiceBet,
    CardHighLowSettings, CardHighLowRound,
    AndarBaharSettings, AndarBaharBet, RouletteSettings, RouletteBet,
    SicBoSettings, SicBoBet, TeenPattiSettings, TeenPattiBet,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'age', 'is_above_18', 'agreed_to_terms', 'created_at')
    search_fields = ('user__username', 'phone_number')
    list_filter = ('is_above_18', 'agreed_to_terms')


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('updated_at',)


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'txn_type', 'amount', 'description', 'created_at')
    list_filter = ('txn_type',)
    search_fields = ('wallet__user__username', 'description')
    readonly_fields = ('created_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'method', 'transaction_id', 'created_at')
    list_filter = ('status', 'method')
    search_fields = ('user__username', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SpinWallet)
class SpinWalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'spins', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = ('updated_at',)


@admin.register(SpinPurchase)
class SpinPurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'spins_purchased', 'amount', 'status', 'razorpay_order_id', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'razorpay_order_id', 'razorpay_payment_id')
    readonly_fields = ('created_at',)


class RazorpaySettingsForm(forms.ModelForm):
    class Meta:
        model = RazorpaySettings
        fields = '__all__'
        widgets = {
            'key_secret': forms.PasswordInput(render_value=True),
        }


@admin.register(RazorpaySettings)
class RazorpaySettingsAdmin(admin.ModelAdmin):
    form = RazorpaySettingsForm
    list_display = ('key_id', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        # Singleton row (pk=1) — created lazily via get_singleton().
        return not RazorpaySettings.objects.exists()


@admin.register(SpinMachineSettings)
class SpinMachineSettingsAdmin(admin.ModelAdmin):
    list_display = ('spin_pack_spins', 'spin_pack_amount', 'homepage_jackpot_display', 'is_active', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        # Singleton row (pk=1) — created lazily via get_singleton().
        return not SpinMachineSettings.objects.exists()


@admin.register(CoinFlipSettings)
class CoinFlipSettingsAdmin(admin.ModelAdmin):
    list_display = ('win_multiplier', 'min_bet', 'max_bet', 'is_active', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        # Singleton row (pk=1) — created lazily via get_singleton().
        return not CoinFlipSettings.objects.exists()


@admin.register(CoinFlipBet)
class CoinFlipBetAdmin(admin.ModelAdmin):
    list_display = ('user', 'bet_amount', 'choice', 'result', 'won', 'payout', 'created_at')
    list_filter = ('won', 'choice')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)


@admin.register(DiceSettings)
class DiceSettingsAdmin(admin.ModelAdmin):
    list_display = ('house_edge_percent', 'min_bet', 'max_bet', 'is_active', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        # Singleton row (pk=1) — created lazily via get_singleton().
        return not DiceSettings.objects.exists()


@admin.register(DiceBet)
class DiceBetAdmin(admin.ModelAdmin):
    list_display = ('user', 'bet_amount', 'direction', 'target', 'roll', 'won', 'multiplier', 'payout', 'created_at')
    list_filter = ('won', 'direction')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)


@admin.register(CardHighLowSettings)
class CardHighLowSettingsAdmin(admin.ModelAdmin):
    list_display = ('house_edge_percent', 'min_bet', 'max_bet', 'is_active', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        # Singleton row (pk=1) — created lazily via get_singleton().
        return not CardHighLowSettings.objects.exists()


@admin.register(CardHighLowRound)
class CardHighLowRoundAdmin(admin.ModelAdmin):
    list_display = ('user', 'bet_amount', 'current_rank', 'current_suit', 'status', 'choice', 'next_rank', 'won', 'payout', 'created_at')
    list_filter = ('status', 'won', 'choice')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'resolved_at')


@admin.register(AndarBaharSettings)
class AndarBaharSettingsAdmin(admin.ModelAdmin):
    list_display = ('win_multiplier', 'min_bet', 'max_bet', 'is_active', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        return not AndarBaharSettings.objects.exists()


@admin.register(AndarBaharBet)
class AndarBaharBetAdmin(admin.ModelAdmin):
    list_display = ('user', 'bet_amount', 'choice', 'result', 'won', 'payout', 'created_at')
    list_filter = ('won', 'choice')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)


@admin.register(RouletteSettings)
class RouletteSettingsAdmin(admin.ModelAdmin):
    list_display = ('house_edge_percent', 'min_bet', 'max_bet', 'is_active', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        return not RouletteSettings.objects.exists()


@admin.register(RouletteBet)
class RouletteBetAdmin(admin.ModelAdmin):
    list_display = ('user', 'bet_amount', 'bet_type', 'bet_value', 'result_number', 'result_color', 'won', 'multiplier', 'payout', 'created_at')
    list_filter = ('won', 'bet_type')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)


@admin.register(SicBoSettings)
class SicBoSettingsAdmin(admin.ModelAdmin):
    list_display = ('house_edge_percent', 'min_bet', 'max_bet', 'is_active', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        return not SicBoSettings.objects.exists()


@admin.register(SicBoBet)
class SicBoBetAdmin(admin.ModelAdmin):
    list_display = ('user', 'bet_amount', 'choice', 'die1', 'die2', 'die3', 'total', 'won', 'multiplier', 'payout', 'created_at')
    list_filter = ('won', 'choice')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)


@admin.register(TeenPattiSettings)
class TeenPattiSettingsAdmin(admin.ModelAdmin):
    list_display = ('win_multiplier', 'min_bet', 'max_bet', 'is_active', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        return not TeenPattiSettings.objects.exists()


@admin.register(TeenPattiBet)
class TeenPattiBetAdmin(admin.ModelAdmin):
    list_display = ('user', 'bet_amount', 'player_hand_type', 'dealer_hand_type', 'outcome', 'payout', 'created_at')
    list_filter = ('outcome', 'player_hand_type')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
