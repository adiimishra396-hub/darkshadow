from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('contact/', views.contact_submit, name='contact_submit'),

    # Wallet
    path('add-money/', views.add_money_view, name='add_money'),
    path('my-wallet/', views.my_wallet_view, name='my_wallet'),
    path('wallet/create-order/', views.wallet_create_order, name='wallet_create_order'),
    path('wallet/verify-payment/', views.wallet_verify_payment, name='wallet_verify_payment'),

    # Profile
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('change-password/', views.change_password_view, name='change_password'),

    # Admin
    path('admin-panel/', views.admin_panel_view, name='admin_panel'),
    path('admin-panel/save-razorpay/', views.save_razorpay_settings, name='save_razorpay_settings'),
    path('admin-panel/save-spin-settings/', views.save_spin_settings, name='save_spin_settings'),
    path('admin-panel/toggle-site-disabled/', views.toggle_site_disabled, name='toggle_site_disabled'),
    path('admin-panel/save-smtp/', views.save_smtp_settings, name='save_smtp_settings'),
    path('admin-panel/toggle-user/<int:user_id>/', views.toggle_user_active, name='toggle_user_active'),
    path('admin-panel/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin-panel/add-user/', views.admin_add_user, name='admin_add_user'),
    path('admin-panel/toggle-contact/<int:message_id>/', views.toggle_contact_resolved, name='toggle_contact_resolved'),
    path('admin-panel/save-customization/', views.save_site_customization, name='save_site_customization'),
    path('admin-panel/save-pwa-settings/', views.save_pwa_settings, name='save_pwa_settings'),
    path('admin-info/', views.admin_info_view, name='admin_info'),

    # PWA
    path('manifest.webmanifest', views.pwa_manifest_view, name='pwa_manifest'),
    path('sw.js', views.service_worker_view, name='service_worker'),

    # Jackpot / Spin Machine
    path('jackpot/create-order/', views.jackpot_create_order, name='jackpot_create_order'),
    path('jackpot/buy-with-wallet/', views.jackpot_buy_with_wallet, name='jackpot_buy_with_wallet'),
    path('jackpot/verify-payment/', views.jackpot_verify_payment, name='jackpot_verify_payment'),
    path('jackpot/use-spin/', views.jackpot_use_spin, name='jackpot_use_spin'),
    path('jackpot/claim-win/', views.jackpot_claim_win, name='jackpot_claim_win'),

    # Coin Flip
    path('coinflip/play/', views.coinflip_play, name='coinflip_play'),

    # Dice Roll
    path('dice/play/', views.dice_play, name='dice_play'),

    # Card High-Low
    path('cardhilo/deal/', views.cardhilo_deal, name='cardhilo_deal'),
    path('cardhilo/resolve/', views.cardhilo_resolve, name='cardhilo_resolve'),

    # Andar Bahar
    path('andarbahar/play/', views.andarbahar_play, name='andarbahar_play'),

    # Roulette
    path('roulette/play/', views.roulette_play, name='roulette_play'),

    # Sic Bo
    path('sicbo/play/', views.sicbo_play, name='sicbo_play'),

    # Teen Patti
    path('teenpatti/play/', views.teenpatti_play, name='teenpatti_play'),

    # Blackjack
    path('blackjack/deal/', views.blackjack_deal, name='blackjack_deal'),
    path('blackjack/hit/', views.blackjack_hit, name='blackjack_hit'),
    path('blackjack/stand/', views.blackjack_stand, name='blackjack_stand'),

    # Baccarat
    path('baccarat/play/', views.baccarat_play, name='baccarat_play'),

    # Poker
    path('poker/play/', views.poker_play, name='poker_play'),

    # Rummy
    path('rummy/play/', views.rummy_play, name='rummy_play'),

    # Crash
    path('crash/bet/', views.crash_bet, name='crash_bet'),
    path('crash/status/', views.crash_status, name='crash_status'),
    path('crash/cashout/', views.crash_cashout, name='crash_cashout'),
]
