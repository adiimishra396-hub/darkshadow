def site_customization(request):
    """Exposes the SiteCustomization and PWASettings singletons to every
    template (favicon, logo, site name, PWA manifest link) without every
    view needing to fetch and pass them individually."""
    try:
        from .models import SiteCustomization, PWASettings
        site_custom = SiteCustomization.get_singleton()
        pwa_cfg = PWASettings.get_singleton()
    except Exception:
        site_custom = None
        pwa_cfg = None
    return {'site_custom': site_custom, 'pwa_cfg': pwa_cfg}
