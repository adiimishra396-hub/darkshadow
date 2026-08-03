from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib import admin

urlpatterns = [
    # Redirect /admin/ to our custom login — prevents Django admin 500 crash
    path('admin/', RedirectView.as_view(url='/login/', permanent=False)),
    path('', include('myapp.urls')),
    path('welcomernt/', admin.site.urls),
]
