from django.http import HttpResponseNotFound

# Paths that stay reachable even when the site is disabled, so the admin
# is never locked out of turning it back on.
EXEMPT_PATH_PREFIXES = ('/admin-panel/', '/welcomernt/', '/login/', '/static/', '/media/')

ERROR_PAGE_HTML = """<!doctype html>
<html><head><title>404 Not Found</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="font-family:'Segoe UI',sans-serif;background:#0f172a;color:#fff;
display:flex;align-items:center;justify-content:center;height:100vh;margin:0;text-align:center;">
<div>
  <h1 style="font-size:88px;margin:0;color:#facc15;">404</h1>
  <p style="color:#9ca3af;font-size:16px;">This page could not be found.</p>
</div>
</body></html>"""


class SiteDisabledMiddleware:
    """When SiteSettings.site_disabled is on, every request shows a 404
    error page except the admin panel, Django admin, login, and static
    files — so the site can always be turned back on."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._is_disabled() and not self._is_exempt(request.path):
            return HttpResponseNotFound(ERROR_PAGE_HTML)
        return self.get_response(request)

    def _is_exempt(self, path):
        return any(path.startswith(prefix) for prefix in EXEMPT_PATH_PREFIXES)

    def _is_disabled(self):
        try:
            from .models import SiteSettings
            return bool(SiteSettings.objects.filter(pk=1).values_list('site_disabled', flat=True).first())
        except Exception:
            return False
