from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

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
    path('admin-panel/toggle-user/<int:user_id>/', views.toggle_user_active, name='toggle_user_active'),
    path('admin-panel/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin-panel/add-user/', views.admin_add_user, name='admin_add_user'),
    path('admin-info/', views.admin_info_view, name='admin_info'),

    # Jackpot / Spin Machine
    path('jackpot/create-order/', views.jackpot_create_order, name='jackpot_create_order'),
    path('jackpot/buy-with-wallet/', views.jackpot_buy_with_wallet, name='jackpot_buy_with_wallet'),
    path('jackpot/verify-payment/', views.jackpot_verify_payment, name='jackpot_verify_payment'),
    path('jackpot/use-spin/', views.jackpot_use_spin, name='jackpot_use_spin'),
    path('jackpot/claim-win/', views.jackpot_claim_win, name='jackpot_claim_win'),

    # Coin Flip
    path('coinflip/play/', views.coinflip_play, name='coinflip_play'),
]
