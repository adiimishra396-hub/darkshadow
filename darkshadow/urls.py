from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.contrib import admin
from myapp.views import page_not_found_view

urlpatterns = [
    # Redirect /admin/ to our custom login — prevents Django admin 500 crash
    path('admin/', RedirectView.as_view(url='/login/', permanent=False)),
    path('', include('myapp.urls')),
    path('welcomernt/', admin.site.urls),
]

# Media (uploaded logos/favicons/PWA icons) — served directly rather than
# gated behind DEBUG since this app has no separate media host/CDN.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Catch-all: any URL that didn't match a route above shows a real 404 page.
# Placed last so it never shadows a real route. A plain handler404 isn't
# enough here because DEBUG=True makes Django show its technical traceback
# page for unmatched URLs regardless of handler404 — this catch-all IS a
# match, so that debug page never triggers.
urlpatterns += [re_path(r'^.*$', page_not_found_view)]

handler404 = page_not_found_view
