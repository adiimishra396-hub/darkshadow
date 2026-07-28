from django.urls import path
from myapp import views

urlpatterns = [
    path('',                                   views.home,                     name='home'),
    path('login/',                             views.login_view,               name='login'),
    path('signup/',                            views.signup_view,              name='signup'),
    path('logout/',                            views.logout_view,              name='logout'),
    # Admin
    path('ds-admin/',                          views.admin_panel_view,         name='admin_panel'),
    path('admin-info/',                        views.admin_info_view,          name='admin_info'),
    path('ds-admin/toggle-user/<int:user_id>/',views.toggle_user_active,       name='toggle_user_active'),
    path('ds-admin/delete-user/<int:user_id>/',views.delete_user,              name='delete_user'),
    path('ds-admin/add-user/',                 views.admin_add_user,           name='admin_add_user'),
    path('ds-admin/razorpay-settings/',        views.save_razorpay_settings,   name='save_razorpay_settings'),
    # Wallet
    path('add-money/',                         views.add_money_view,           name='add_money'),
    path('wallet/create-order/',               views.wallet_create_order,      name='wallet_create_order'),
    path('wallet/verify-payment/',             views.wallet_verify_payment,    name='wallet_verify_payment'),
    path('my-wallet/',                         views.my_wallet_view,           name='my_wallet'),
    # Profile
    path('edit-profile/',                      views.edit_profile_view,        name='edit_profile'),
    path('change-password/',                   views.change_password_view,     name='change_password'),
    # Jackpot
    path('jackpot/create-order/',              views.jackpot_create_order,     name='jackpot_create_order'),
    path('jackpot/verify-payment/',            views.jackpot_verify_payment,   name='jackpot_verify_payment'),
    path('jackpot/use-spin/',                  views.jackpot_use_spin,         name='jackpot_use_spin'),
]
