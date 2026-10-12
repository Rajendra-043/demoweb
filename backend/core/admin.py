"""Admin configuration -- every piece of page content is editable here."""

from django.contrib import admin, messages
from django.utils.html import format_html

from .models import (
    Accommodation,
    Competition,
    ContactMessage,
    Event,
    EventCategory,
    FAQ,
    NavigationItem,
    Organiser,
    Page,
    PageSection,
    Registration,
    SectionItem,
    SiteSettings,
    SocialLink,
    Sponsor,
    Workshop,
)


class SectionItemInline(admin.TabularInline):
    model = SectionItem
    extra = 1
    fields = (
        "title",
        "subtitle",
        "icon",
        "image",
        "meta_left",
        "meta_right",
        "button_label",
        "url",
        "order",
        "is_visible",
    )


class PageSectionInline(admin.StackedInline):
    model = PageSection
    extra = 0
    show_change_link = True
    fields = (
        "title",
        "kicker",
        "subtitle",
        "layout",
        "align",
        "columns",
        "body",
        "button_label",
        "button_url",
        "background_image",
        "is_visible",
        "order",
    )


class FAQInline(admin.TabularInline):
    model = FAQ
    extra = 1
    fields = ("question", "answer", "order", "is_visible")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "organisation", "hero_title", "updated_at")

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    fieldsets = (
        ("Identity", {"fields": ("site_name", "logo_text", "logo_superscript", "organisation")}),
        ("Home hero", {"fields": ("hero_eyebrow", "hero_title", "hero_meta_left", "hero_meta_right",
                                   "hero_description", "hero_tagline", "primary_button_label",
                                   "primary_button_url", "secondary_button_label", "trailer_url",
                                   "trailer_poster")}),
        ("Background", {"fields": ("background_image", "background_overlay")}),
        ("Footer & contact", {"fields": ("footer_tagline", "footer_copyright", "contact_email",
                                         "contact_phone", "contact_address", "map_embed_url")}),
        ("SEO", {"fields": ("meta_description", "meta_keywords")}),
    )


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "template", "is_published", "show_in_header", "order")
    list_filter = ("template", "is_published", "show_in_header", "show_in_side_panel")
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PageSectionInline, FAQInline]
    fieldsets = (
        ("Page", {"fields": ("title", "slug", "template", "order")}),
        ("Hero copy", {"fields": ("eyebrow", "hero_title", "meta_left", "meta_right", "description",
                                  "tagline", "hero_image", "show_scroll_indicator")}),
        ("Body", {"fields": ("body",)}),
        ("Visibility", {"fields": ("is_published", "show_in_header", "show_in_side_panel",
                                   "allow_in_site_map")}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
    )


@admin.register(PageSection)
class PageSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "page", "layout", "columns", "is_visible", "order")
    list_filter = ("page", "layout", "is_visible")
    search_fields = ("title", "body", "page__title")
    list_editable = ("is_visible", "order")
    inlines = [SectionItemInline]


@admin.register(NavigationItem)
class NavigationItemAdmin(admin.ModelAdmin):
    list_display = ("label", "position", "target", "icon", "is_active", "order")
    list_filter = ("position", "is_active")
    list_editable = ("is_active", "order", "icon")
    search_fields = ("label", "url")


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("network", "label", "url", "icon", "is_active", "order")
    list_editable = ("is_active", "order", "icon")
    list_filter = ("network", "is_active")


class PosterMixin:
    def poster_tag(self, obj):
        for field in ("poster", "image", "logo", "photo"):
            media = getattr(obj, field, None)
            if media:
                return format_html('<img src="{}" style="height:56px;border-radius:6px" />', media.url)
        return "—"

    poster_tag.short_description = "Preview"


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Event)
class EventAdmin(PosterMixin, admin.ModelAdmin):
    list_display = ("title", "category", "start_at", "venue", "is_featured", "is_published", "order")
    list_filter = ("is_published", "is_featured", "category")
    search_fields = ("title", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("is_featured", "is_published", "order")
    readonly_fields = ("poster_tag",)
    fieldsets = (
        ("Event", {"fields": ("title", "slug", "category", "summary", "body")}),
        ("When & where", {"fields": ("start_at", "end_at", "venue")}),
        ("Media & links", {"fields": ("poster_tag", "poster", "registration_url", "contact_email")}),
        ("Publishing", {"fields": ("is_published", "is_featured", "order")}),
    )


@admin.register(Workshop)
class WorkshopAdmin(PosterMixin, admin.ModelAdmin):
    list_display = ("title", "track", "instructor", "date", "seats", "is_published", "is_featured", "order")
    list_filter = ("is_published", "is_featured", "track")
    search_fields = ("title", "track", "instructor", "summary")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("is_published", "is_featured", "order")
    readonly_fields = ("image_tag",)

    def image_tag(self, obj):
        return self.poster_tag(obj)

    image_tag.short_description = "Preview"


@admin.register(Competition)
class CompetitionAdmin(PosterMixin, admin.ModelAdmin):
    list_display = ("title", "category", "deadline", "prize", "is_published", "is_featured", "order")
    list_filter = ("is_published", "is_featured", "category")
    search_fields = ("title", "category", "summary")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("is_published", "is_featured", "order")


@admin.register(Accommodation)
class AccommodationAdmin(PosterMixin, admin.ModelAdmin):
    list_display = ("name", "kind", "distance_from_campus", "price_per_night", "is_available",
                    "is_published", "order")
    list_filter = ("kind", "is_available", "is_published")
    search_fields = ("name", "summary", "amenities")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_available", "is_published", "order")


@admin.register(Sponsor)
class SponsorAdmin(PosterMixin, admin.ModelAdmin):
    list_display = ("name", "tier", "is_published", "order")
    list_filter = ("tier", "is_published")
    list_editable = ("is_published", "order")


@admin.register(Organiser)
class OrganiserAdmin(PosterMixin, admin.ModelAdmin):
    list_display = ("name", "role", "is_visible", "order")
    list_editable = ("is_visible", "order")
    readonly_fields = ("photo_tag",)

    def photo_tag(self, obj):
        return self.poster_tag(obj)

    photo_tag.short_description = "Preview"


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "page", "order", "is_visible")
    list_editable = ("order", "is_visible")
    search_fields = ("question", "answer")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at", "is_handled")
    list_filter = ("is_handled", "created_at")
    list_editable = ("is_handled",)
    search_fields = ("name", "email", "message")
    readonly_fields = ("created_at",)
    actions = ["mark_handled"]

    @admin.action(description="Mark selected messages as handled")
    def mark_handled(self, request, queryset):
        updated = queryset.update(is_handled=True)
        self.message_user(request, f"{updated} message(s) marked as handled.", messages.SUCCESS)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "college", "interest", "created_at")
    list_filter = ("interest", "created_at")
    search_fields = ("full_name", "email", "college")
    readonly_fields = ("created_at",)


admin.site.site_header = "OJUS administration"
admin.site.site_title = "OJUS admin"
admin.site.index_title = "Manage OJUS content"
