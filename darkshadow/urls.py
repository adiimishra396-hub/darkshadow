from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib import admin

urlpatterns = [
    # Redirect /admin/ to our custom login — prevents Django admin 500 crash
    path('admin/', RedirectView.as_view(url='/login/', permanent=False)),
    path('', include('myapp.urls')),
    path('welcomernt/', admin.site.urls),
]

# Media (uploaded logos/favicons/PWA icons) — served directly rather than
# gated behind DEBUG since this app has no separate media host/CDN.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
