"""
Data model for the TECNO site.

Design idea
-----------
Almost every visual element on the site is a *model row* you can edit in
/admin/ later:

* ``SiteSettings``  -> logo, hero copy, background image, trailer, footer.
* ``NavigationItem``/``SocialLink`` -> the header bar + the two floating side
  panels. Add/remove/reorder them, no template editing required.
* ``Page`` -> every page on the site (Home, Events, CES, About, Contact,
  Accommodation, Workshops, Competitions, Ignite). Each page carries its own
  hero copy and a list of ``PageSection`` blocks.
* ``PageSection`` -> a reusable "space" on a page (heading + body + grid of
  ``SectionItem`` cards). Create them empty and they still render as a titled
  placeholder panel, so you can fill them in whenever you want.
* Domain models (``Event``, ``Workshop``, ``Competition``, ``Accommodation``,
  ``Sponsor``, ``Organiser``, ``FAQ``) back the auto-generated listing pages.
* ``ContactMessage`` stores contact form submissions for the admin inbox.
* ``Registration`` stores attendee sign-ups.
"""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


# ---------------------------------------------------------------------------
# Base helpers
# ---------------------------------------------------------------------------


class TimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Publishable(TimeStamped):
    """Adds draft/publish switching plus a free ordering column."""

    is_published = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        abstract = True


def slug_for(instance, value, model=None):
    """Slug generator that ignores the instance's own current row on save."""
    model = model or instance.__class__
    base = slugify(value) or "item"
    slug, i = base, 2
    if instance.pk:
        queryset = model._default_manager.exclude(pk=instance.pk)
    else:
        queryset = model._default_manager.all()
    while queryset.filter(slug=slug).exists():
        slug = f"{base}-{i}"
        i += 1
    return slug


# Upload paths. These must be real module-level functions (not lambdas or
# closures) so Django can serialise them into migrations.


def background_upload_to(instance, filename):
    return f"background/{timezone.now():%Y/%m}/{filename}"


def trailer_upload_to(instance, filename):
    return f"trailer/{timezone.now():%Y/%m}/{filename}"


def page_upload_to(instance, filename):
    return f"pages/{timezone.now():%Y/%m}/{filename}"


def section_upload_to(instance, filename):
    return f"sections/{timezone.now():%Y/%m}/{filename}"


def section_item_upload_to(instance, filename):
    return f"sections/items/{timezone.now():%Y/%m}/{filename}"


def event_upload_to(instance, filename):
    return f"events/{timezone.now():%Y/%m}/{filename}"


def workshop_upload_to(instance, filename):
    return f"workshops/{timezone.now():%Y/%m}/{filename}"


def competition_upload_to(instance, filename):
    return f"competitions/{timezone.now():%Y/%m}/{filename}"


def accommodation_upload_to(instance, filename):
    return f"accommodation/{timezone.now():%Y/%m}/{filename}"


def organiser_upload_to(instance, filename):
    return f"organisers/{timezone.now():%Y/%m}/{filename}"


def sponsor_upload_to(instance, filename):
    return f"sponsors/{timezone.now():%Y/%m}/{filename}"


# ---------------------------------------------------------------------------
# Global site content
# ---------------------------------------------------------------------------


class SiteSettings(TimeStamped):
    """Singleton row (pk=1) holding everything global to the site."""

    site_name = models.CharField(max_length=120, default="TECNO")
    logo_text = models.CharField(max_length=40, default="TECNO")
    logo_superscript = models.CharField(max_length=10, default="™")
    organisation = models.CharField(max_length=160, blank=True, default="My College's")

    # Hero (the block in the middle of the landing page)
    hero_eyebrow = models.CharField(max_length=160, blank=True, default="My College's")
    hero_title = models.CharField(max_length=160, default="TECNO")
    hero_meta_left = models.CharField(max_length=120, blank=True, default="16th – 18th December")
    hero_meta_right = models.CharField(max_length=120, blank=True, default="30th Edition")
    hero_description = models.CharField(
        max_length=300,
        blank=True,
        default="ASIA'S LARGEST SCIENCE & TECHNOLOGY FESTIVAL",
    )
    hero_tagline = models.CharField(max_length=160, blank=True, default="— An Aetherial Renaissance —")

    primary_button_label = models.CharField(max_length=60, default="EXPLORE TECNO")
    primary_button_url = models.CharField(max_length=200, blank=True, default="/events/")
    secondary_button_label = models.CharField(max_length=60, default="WATCH TRAILER")
    trailer_url = models.URLField(blank=True, help_text="YouTube / Vimeo link for the trailer modal.")
    trailer_poster = models.ImageField(upload_to=trailer_upload_to, blank=True, null=True)

    background_image = models.ImageField(
        upload_to=background_upload_to,
        blank=True,
        null=True,
        help_text="Full-screen cinematic background. Falls back to static/img/background.jpg.",
    )
    background_overlay = models.CharField(
        max_length=12, default="#080b18", help_text="Fallback colour behind the background image."
    )

    # Footer
    footer_tagline = models.CharField(max_length=200, blank=True)
    footer_copyright = models.CharField(
        max_length=200, blank=True, default="© TECNO · My College. All rights reserved."
    )
    contact_email = models.EmailField(blank=True, default="tecno@mycollege.edu.in")
    contact_phone = models.CharField(max_length=40, blank=True)
    contact_address = models.TextField(blank=True)
    map_embed_url = models.URLField(blank=True, help_text="Google Maps embed src URL.")

    # SEO
    meta_description = models.CharField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        return super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Page(TimeStamped):
    """
    Every page of the site.

    ``template`` picks which layout renders the page; ``PageSection`` rows
    provide the editable "spaces" underneath the hero.
    """

    class Template(models.TextChoices):
        STANDARD = "standard", "Standard (hero + sections)"
        HOME = "home", "Home landing page"
        EVENTS = "events", "Events listing"
        CES = "ces", "CES showcase"
        ABOUT = "about", "About us"
        CONTACT = "contact", "Contact (with form)"
        ACCOMMODATION = "accommodation", "Accommodation listing"
        WORKSHOPS = "workshops", "Workshops listing"
        COMPETITIONS = "competitions", "Competitions listing"
        IGNITE = "ignite", "Ignite programme"
        REQUIREMENTS = "requirements", "Requirements & eligibility"

    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True)
    template = models.CharField(max_length=20, choices=Template.choices, default=Template.STANDARD)

    # Hero copy (leave blank to keep the frame but hide the words)
    eyebrow = models.CharField(max_length=160, blank=True)
    hero_title = models.CharField(max_length=160, blank=True)
    meta_left = models.CharField(max_length=120, blank=True)
    meta_right = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    tagline = models.CharField(max_length=200, blank=True)
    hero_image = models.ImageField(upload_to=page_upload_to, blank=True, null=True)
    show_scroll_indicator = models.BooleanField(default=False)

    # Long-form body for STANDARD pages
    body = models.TextField(blank=True)

    # Behaviour
    is_published = models.BooleanField(default=True, db_index=True)
    show_in_header = models.BooleanField(default=False)
    show_in_side_panel = models.BooleanField(default=False)
    allow_in_site_map = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    # SEO
    meta_title = models.CharField(max_length=180, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_for(self, self.title)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:page", kwargs={"slug": self.slug})

    @property
    def is_live(self):
        return self.is_published

    @property
    def hero_heading(self):
        return self.hero_title or self.title

    @property
    def meta_pair(self):
        return [m for m in (self.meta_left, self.meta_right) if m]


class NavigationItem(TimeStamped):
    """Links for the glass navbar and the two floating side panels."""

    class Position(models.TextChoices):
        HEADER = "header", "Top navbar"
        LEFT = "left", "Left side panel"
        RIGHT = "right", "Right side panel"
        FOOTER = "footer", "Footer"

    label = models.CharField(max_length=60)
    position = models.CharField(max_length=10, choices=Position.choices, default=Position.HEADER)
    url = models.CharField(
        max_length=200,
        blank=True,
        help_text="Leave blank to auto-resolve from the linked page.",
    )
    page = models.ForeignKey(
        "Page", null=True, blank=True, on_delete=models.SET_NULL, related_name="nav_items"
    )
    icon = models.CharField(max_length=8, blank=True, help_text="Single glyph, e.g. ⌂ ▦ ◈")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    open_in_new_tab = models.BooleanField(default=False)

    class Meta:
        ordering = ["position", "order", "id"]
        verbose_name = "Navigation link"
        verbose_name_plural = "Navigation links"

    def __str__(self):
        return f"{self.get_position_display()}: {self.label}"

    @property
    def target(self):
        if self.page_id and self.page and self.page.is_live:
            return self.page.get_absolute_url()
        return self.url or "#"


class SocialLink(TimeStamped):
    class Network(models.TextChoices):
        INSTAGRAM = "instagram", "Instagram"
        X = "x", "X (Twitter)"
        LINKEDIN = "linkedin", "LinkedIn"
        FACEBOOK = "facebook", "Facebook"
        YOUTUBE = "youtube", "YouTube"
        GITHUB = "github", "GitHub"
        OTHER = "other", "Other"

    network = models.CharField(max_length=20, choices=Network.choices, default=Network.INSTAGRAM)
    label = models.CharField(max_length=60, blank=True)
    url = models.URLField()
    icon = models.CharField(max_length=8, blank=True, help_text="Single glyph, e.g. ◎ 𝕏 in ▶")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.label or self.get_network_display()


# ---------------------------------------------------------------------------
# Pages + flexible content blocks
# ---------------------------------------------------------------------------


class PageSection(TimeStamped):
    """
    An editable block on a page.

    An empty section still renders a titled glass panel so the page layout is
    visible before you have content -- that is the "space to fill later".
    """

    class Layout(models.TextChoices):
        TEXT = "text", "Text only"
        CARDS = "cards", "Card grid"
        FEATURED = "featured", "Featured / spotlight"
        GALLERY = "gallery", "Image gallery"
        TIMELINE = "timeline", "Timeline"
        STATS = "stats", "Statistics row"
        CTA = "cta", "Call to action banner"
        CHECKLIST = "checklist", "Checklist (tick-off rows)"
        FORM = "form", "Custom form (embed HTML)"

    class Align(models.TextChoices):
        LEFT = "left", "Left"
        CENTER = "center", "Centre"

    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    kicker = models.CharField(max_length=120, blank=True)
    body = models.TextField(blank=True)
    layout = models.CharField(max_length=12, choices=Layout.choices, default=Layout.TEXT)
    align = models.CharField(max_length=6, choices=Align.choices, default=Align.CENTER)
    columns = models.PositiveSmallIntegerField(
        default=3, validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    button_label = models.CharField(max_length=60, blank=True)
    button_url = models.CharField(max_length=200, blank=True)
    background_image = models.ImageField(upload_to=section_upload_to, blank=True, null=True)
    is_visible = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Page section"
        verbose_name_plural = "Page sections"

    def __str__(self):
        return f"{self.page.title} · {self.title}"


class SectionItem(TimeStamped):
    """A card / tile / stat / timeline entry inside a ``PageSection``."""

    section = models.ForeignKey(PageSection, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=200, blank=True)
    body = models.TextField(blank=True)
    icon = models.CharField(max_length=8, blank=True)
    image = models.ImageField(upload_to=section_item_upload_to, blank=True, null=True)
    url = models.CharField(max_length=200, blank=True)
    button_label = models.CharField(max_length=60, blank=True)
    meta_left = models.CharField(max_length=120, blank=True)
    meta_right = models.CharField(max_length=120, blank=True)
    is_visible = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title or f"Item {self.pk}"


class FAQ(TimeStamped):
    question = models.CharField(max_length=300)
    answer = models.TextField(blank=True)
    page = models.ForeignKey(
        Page, blank=True, null=True, on_delete=models.CASCADE, related_name="faqs"
    )
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.question


# ---------------------------------------------------------------------------
# Domain content
# ---------------------------------------------------------------------------


class EventCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Event categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_for(self, self.name)
        return super().save(*args, **kwargs)


class Event(Publishable):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(
        EventCategory, blank=True, null=True, on_delete=models.SET_NULL, related_name="events"
    )
    summary = models.CharField(max_length=300, blank=True)
    body = models.TextField(blank=True)
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)
    venue = models.CharField(max_length=160, blank=True)
    poster = models.ImageField(upload_to=event_upload_to, blank=True, null=True)
    registration_url = models.CharField(max_length=300, blank=True)
    contact_email = models.EmailField(blank=True)

    class Meta:
        ordering = ["order", "start_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_for(self, self.title)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:event_detail", kwargs={"slug": self.slug})

    @property
    def is_upcoming(self):
        return bool(self.start_at and self.start_at >= timezone.now())


class Workshop(Publishable):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    track = models.CharField(max_length=120, blank=True)
    instructor = models.CharField(max_length=160, blank=True)
    summary = models.CharField(max_length=300, blank=True)
    body = models.TextField(blank=True)
    date = models.DateField(blank=True, null=True)
    time_slot = models.CharField(max_length=80, blank=True)
    venue = models.CharField(max_length=160, blank=True)
    duration = models.CharField(max_length=60, blank=True)
    seats = models.PositiveIntegerField(default=0, help_text="0 = unlimited / not set")
    price = models.CharField(max_length=60, blank=True)
    difficulty = models.CharField(max_length=40, blank=True)
    image = models.ImageField(upload_to=workshop_upload_to, blank=True, null=True)
    registration_url = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["order", "date", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_for(self, self.title)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:workshop_detail", kwargs={"slug": self.slug})


class Competition(Publishable):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(max_length=120, blank=True)
    summary = models.CharField(max_length=300, blank=True)
    body = models.TextField(blank=True)
    rules = models.TextField(blank=True)
    prize = models.CharField(max_length=200, blank=True)
    deadline = models.DateField(blank=True, null=True)
    venue = models.CharField(max_length=160, blank=True)
    team_size = models.CharField(max_length=60, blank=True)
    image = models.ImageField(upload_to=competition_upload_to, blank=True, null=True)
    registration_url = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["order", "deadline", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_for(self, self.title)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:competition_detail", kwargs={"slug": self.slug})


class Accommodation(Publishable):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    kind = models.CharField(
        max_length=40,
        choices=[
            ("hostel", "Hostel"),
            ("hotel", "Hotel"),
            ("guesthouse", "Guest house"),
            ("resort", "Resort"),
            ("camping", "Camping"),
        ],
        default="hostel",
    )
    summary = models.CharField(max_length=300, blank=True)
    body = models.TextField(blank=True)
    distance_from_campus = models.CharField(max_length=80, blank=True, help_text="e.g. 1.2 km")
    price_per_night = models.CharField(max_length=60, blank=True)
    amenities = models.CharField(max_length=300, blank=True, help_text="Comma separated.")
    capacity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    check_in = models.CharField(max_length=40, blank=True)
    check_out = models.CharField(max_length=40, blank=True)
    image = models.ImageField(upload_to=accommodation_upload_to, blank=True, null=True)
    booking_url = models.CharField(max_length=300, blank=True)
    contact_email = models.EmailField(blank=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_for(self, self.name)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:accommodation_detail", kwargs={"slug": self.slug})

    @property
    def amenity_list(self):
        return [a.strip() for a in self.amenities.split(",") if a.strip()]

    @property
    def title(self):
        """Alias so shared templates can treat every content type alike."""
        return self.name


class Organiser(TimeStamped):
    name = models.CharField(max_length=160)
    role = models.CharField(max_length=160, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to=organiser_upload_to, blank=True, null=True)
    email = models.EmailField(blank=True)
    linkedin = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Sponsor(Publishable):
    name = models.CharField(max_length=160)
    tier = models.CharField(
        max_length=30,
        choices=[
            ("title", "Title sponsor"),
            ("platinum", "Platinum"),
            ("gold", "Gold"),
            ("silver", "Silver"),
            ("partner", "Partner"),
        ],
        default="partner",
    )
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to=sponsor_upload_to, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["tier", "order", "name"]

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# User generated content
# ---------------------------------------------------------------------------


class ContactMessage(models.Model):
    name = models.CharField(max_length=160)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    page = models.ForeignKey(
        Page, blank=True, null=True, on_delete=models.SET_NULL, related_name="messages"
    )
    is_handled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Registration(models.Model):
    """Attendee sign-up captured from any page form."""

    class Interest(models.TextChoices):
        GENERAL = "general", "General pass"
        EVENT = "event", "Event"
        WORKSHOP = "workshop", "Workshop"
        COMPETITION = "competition", "Competition"
        ACCOMMODATION = "accommodation", "Accommodation"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="registrations",
    )
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    college = models.CharField(max_length=200, blank=True)
    interest = models.CharField(max_length=20, choices=Interest.choices, default=Interest.GENERAL)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Registration"
        verbose_name_plural = "Registrations"

    def __str__(self):
        return f"{self.full_name} ({self.get_interest_display()})"
