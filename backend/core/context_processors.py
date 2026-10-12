from django.conf import settings

from .models import NavigationItem, Page, SiteSettings, SocialLink


def site_context(request):
    """Makes site settings + navigation available to every template."""
    site = SiteSettings.load()
    return {
        "site": site,
        "header_links": NavigationItem.objects.filter(
            position=NavigationItem.Position.HEADER, is_active=True
        ),
        "left_links": NavigationItem.objects.filter(
            position=NavigationItem.Position.LEFT, is_active=True
        ),
        "right_links": NavigationItem.objects.filter(
            position=NavigationItem.Position.RIGHT, is_active=True
        ),
        "footer_links": NavigationItem.objects.filter(
            position=NavigationItem.Position.FOOTER, is_active=True
        ),
        "social_links": SocialLink.objects.filter(is_active=True),
        "all_pages": Page.objects.filter(is_published=True),
        "DEBUG": settings.DEBUG,
    }
