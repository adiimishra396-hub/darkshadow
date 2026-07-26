from django.urls import path
from myapp import views

urlpatterns = [
    path('',                  views.home,                name='home'),
    path('login/',            views.login_view,          name='login'),
    path('signup/',           views.signup_view,         name='signup'),
    path('logout/',           views.logout_view,         name='logout'),
    path('ds-admin/',         views.admin_panel_view,    name='admin_panel'),
    path('admin-info/',       views.admin_info_view,     name='admin_info'),
    # Wallet
    path('add-money/',        views.add_money_view,      name='add_money'),
    path('my-wallet/',        views.my_wallet_view,      name='my_wallet'),
    # Profile
    path('edit-profile/',     views.edit_profile_view,   name='edit_profile'),
    path('change-password/',  views.change_password_view, name='change_password'),
]
