"""
Default site provisioning.

This is deliberately written against an ``apps`` registry rather than importing
``core.models`` directly, so the exact same code can run from:

* ``python manage.py seed_site``      (real models)
* the ``core.0003_provision_default_pages`` data migration (historical models)

That matters because a fresh deployment -- e.g. a new Render dyno with an empty
database -- has no ``Page`` rows at all. Without provisioning on migrate the
home view 404s on every request, because the site is driven by DB rows.

Only string literals are used for choice values (never ``Page.Template.HOME``)
so this stays valid when models are frozen in time by a migration.
"""

from django.utils.text import slugify

HEADER = "header"
LEFT = "left"
FOOTER = "footer"

PAGE_SEED = [
    {
        "slug": "home",
        "title": "Home",
        "template": "home",
        "eyebrow": "My College's",
        "hero_title": "TECNO",
        "meta_left": "16th – 18th December",
        "meta_right": "30th Edition",
        "description": "ASIA'S LARGEST SCIENCE & TECHNOLOGY FESTIVAL",
        "tagline": "— An Aetherial Renaissance —",
        "show_in_side_panel": True,
        "order": 0,
        "sections": [
            {
                "title": "What is TECNO",
                "kicker": "The festival",
                "subtitle": "Three days of talks, builds, contests and experiments.",
                "layout": "text",
                "body": (
                    "TECNO is the annual science and technology festival of My College. "
                    "Replace this paragraph with your own introduction — it lives in the admin "
                    "under Pages › Home › What is TECNO."
                ),
            },
            {
                "title": "By the numbers",
                "kicker": "Last edition",
                "layout": "stats",
                "columns": 4,
                "items": [
                    {"title": "30", "subtitle": "Editions"},
                    {"title": "40K+", "subtitle": "Visitors"},
                    {"title": "120+", "subtitle": "Events"},
                    {"title": "60", "subtitle": "Colleges"},
                ],
            },
            {
                "title": "What you can do here",
                "kicker": "Explore",
                "layout": "cards",
                "columns": 3,
                "items": [
                    {"icon": "▦", "title": "Events", "subtitle": "Keynotes & showcases",
                     "body": "Talks, demos and exhibitions across every department.",
                     "button_label": "Browse events", "url": "/events/"},
                    {"icon": "◉", "title": "Workshops", "subtitle": "Hands-on labs",
                     "body": "Limited-seat, instructor-led sessions you can book.",
                     "button_label": "See workshops", "url": "/workshops/"},
                    {"icon": "◈", "title": "Competitions", "subtitle": "Build & win",
                     "body": "Hardware, software and design challenges with prizes.",
                     "button_label": "View competitions", "url": "/competitions/"},
                ],
            },
        ],
    },
    {
        "slug": "events",
        "title": "Events",
        "template": "events",
        "eyebrow": "Programme",
        "hero_title": "Events",
        "description": "Keynotes, exhibitions and showcases across all three days.",
        "show_in_side_panel": True,
        "order": 1,
        "sections": [
            {
                "title": "Schedule at a glance",
                "kicker": "Timeline",
                "layout": "timeline",
                "items": [
                    {"title": "Day 1 · Inauguration & opening keynote",
                     "meta_left": "16 Dec", "meta_right": "Morning",
                     "body": "Blank — fill in your schedule here."},
                    {"title": "Day 2 · Workshops & project expo",
                     "meta_left": "17 Dec", "meta_right": "All day",
                     "body": "Blank — fill in your schedule here."},
                    {"title": "Day 3 · Finals & closing ceremony",
                     "meta_left": "18 Dec", "meta_right": "Evening",
                     "body": "Blank — fill in your schedule here."},
                ],
            }
        ],
    },
    {
        "slug": "ces",
        "title": "CES",
        "template": "ces",
        "eyebrow": "Showcase",
        "hero_title": "CES",
        "description": "The TECNO showcase floor — exhibits, demos and product launches.",
        "show_in_side_panel": True,
        "order": 2,
    },
    {
        "slug": "ignite",
        "title": "Ignite",
        "template": "ignite",
        "eyebrow": "Programme",
        "hero_title": "Ignite",
        "description": "The ignition stage — talks that set the festival in motion.",
        "show_in_header": True,
        "order": 3,
    },
    {
        "slug": "workshops",
        "title": "Workshops",
        "template": "workshops",
        "eyebrow": "Learn",
        "hero_title": "Workshops",
        "description": "Small-group, hands-on sessions led by faculty and industry mentors.",
        "show_in_header": True,
        "order": 4,
    },
    {
        "slug": "competitions",
        "title": "Competitions",
        "template": "competitions",
        "eyebrow": "Compete",
        "hero_title": "Competitions",
        "description": "Challenges in hardware, software, design and robotics.",
        "show_in_header": True,
        "order": 5,
    },
    {
        "slug": "accommodation",
        "title": "Accommodation",
        "template": "accommodation",
        "eyebrow": "Stay",
        "hero_title": "Accommodation",
        "description": "Hostels, hotels and camps near the My College campus.",
        "show_in_header": True,
        "order": 6,
    },
    {
        "slug": "about",
        "title": "About Us",
        "template": "about",
        "eyebrow": "Who we are",
        "hero_title": "About Us",
        "description": "The student team and the story behind the festival.",
        "show_in_side_panel": True,
        "order": 7,
        "body": (
            "TECNO is run entirely by students of My College. Replace this text with your "
            "own history, mission and vision — edit it under Pages › About Us."
        ),
    },
    {
        "slug": "contact",
        "title": "Contact Us",
        "template": "contact",
        "eyebrow": "Get in touch",
        "hero_title": "Contact Us",
        "description": "Questions, sponsorships, volunteering or anything else.",
        "show_in_side_panel": True,
        "order": 8,
    },
    {
        "slug": "requirements",
        "title": "Requirements",
        "template": "requirements",
        "eyebrow": "Before you come",
        "hero_title": "Requirements",
        "description": "Who can participate, what to carry, and the ground rules.",
        "tagline": "Everything you need to take part",
        "show_in_side_panel": True,
        "order": 9,
        "sections": [
            {
                "title": "Who can participate",
                "kicker": "Eligibility",
                "layout": "checklist",
                "items": [
                    {"icon": "✓", "title": "Students",
                     "subtitle": "College / school / university",
                     "body": "Open to all students with a valid institutional ID card."},
                    {"icon": "✓", "title": "Faculty & staff",
                     "body": "Institute staff are welcome at all sessions."},
                    {"icon": "✓", "title": "External participants",
                     "body": "Outstation visitors need approval in advance — raise a query and the team will confirm."},
                ],
            },
            {
                "title": "Documents to carry",
                "kicker": "What to bring",
                "layout": "checklist",
                "items": [
                    {"icon": "▤", "title": "Photo ID card",
                     "body": "College ID or any government photo ID — required at every venue gate."},
                    {"icon": "▤", "title": "Registration pass / QR",
                     "body": "Issued after registration. Workshops are strictly pass-limited."},
                    {"icon": "▤", "title": "Consent form",
                     "body": "Signed by a guardian if you are under 18."},
                ],
            },
            {
                "title": "Participation requirements",
                "kicker": "Per programme",
                "layout": "cards",
                "columns": 3,
                "items": [
                    {"icon": "◉", "title": "Workshops", "subtitle": "Limited seats",
                     "body": "Register in advance and arrive 15 minutes early to claim your seat.",
                     "button_label": "See workshops", "url": "/workshops/"},
                    {"icon": "◈", "title": "Competitions", "subtitle": "Team based",
                     "body": "Form a team within the allowed size and submit your entry before the deadline.",
                     "button_label": "See competitions", "url": "/competitions/"},
                    {"icon": "▦", "title": "Exhibitions", "subtitle": "Open entry",
                     "body": "Walk in any time during showcase hours.",
                     "button_label": "See events", "url": "/events/"},
                ],
            },
            {
                "title": "Ground rules",
                "kicker": "Code of conduct",
                "layout": "text",
                "body": (
                    "Add your code of conduct here — photography policy, damage liability, "
                    "submissions must be original, and any rule you want participants to agree to."
                ),
            },
            {
                "title": "Questions?",
                "layout": "cta",
                "align": "center",
                "body": "If anything on this page is unclear, the organising team will help.",
                "button_label": "CONTACT THE TEAM",
                "button_url": "/contact/",
            },
        ],
    },
]

# (position, label, target-slug-or-url, icon)
NAV_SEED = [
    (HEADER, "Accommodation", "accommodation", ""),
    (HEADER, "Workshops", "workshops", ""),
    (HEADER, "Competitions", "competitions", ""),
    (HEADER, "Ignite", "ignite", ""),
    (LEFT, "Home", "home", "⌂"),
    (LEFT, "Events", "events", "▦"),
    (LEFT, "CES", "ces", "◈"),
    (LEFT, "Contact Us", "contact", "♧"),
    (LEFT, "About Us", "about", "ⓘ"),
    (LEFT, "Requirements", "requirements", "✓"),
    (FOOTER, "Requirements", "requirements", ""),
    (FOOTER, "All pages", "/sitemap/", ""),
]

# (network, url, icon)
SOCIAL_SEED = [
    ("instagram", "https://instagram.com", "◎"),
    ("x", "https://x.com", "\U0001d54f"),
    ("linkedin", "https://linkedin.com", "in"),
    ("facebook", "https://facebook.com", "f"),
    ("youtube", "https://youtube.com", "▶"),
]

EVENT_CATEGORIES = ["Keynote", "Exhibition", "Workshop", "Performance"]


def unique_slug(model, value):
    """
    Build a collision-free slug for a model.

    Slugs must be computed explicitly here rather than left to the model's
    ``save()``: Django's migration machinery renders *historical* models
    (``__fake__.Foo``) without custom ``save()`` overrides, so any slug
    generated there would silently be inserted as an empty string and then
    blow up the UNIQUE constraint on the second row.
    """
    base = slugify(value) or "item"
    slug, i = base, 2
    while model._default_manager.filter(slug=slug).exists():
        slug = f"{base}-{i}"
        i += 1
    return slug


def provision_site(apps=None, log=None):
    """
    Create the default site structure. Idempotent: safe to call repeatedly.

    ``apps`` is a Django app registry (historical inside migrations, the real
    one otherwise). ``log`` is an optional callable for progress messages.
    """

    def emit(message):
        if log:
            log(message)

    if apps is None:
        from django.apps import apps as global_apps

        apps = global_apps

    SiteSettings = apps.get_model("core", "SiteSettings")
    Page = apps.get_model("core", "Page")
    PageSection = apps.get_model("core", "PageSection")
    SectionItem = apps.get_model("core", "SectionItem")
    NavigationItem = apps.get_model("core", "NavigationItem")
    SocialLink = apps.get_model("core", "SocialLink")
    EventCategory = apps.get_model("core", "EventCategory")
    Organiser = apps.get_model("core", "Organiser")
    Sponsor = apps.get_model("core", "Sponsor")

    # --- site settings (singleton, pk=1) ---------------------------------
    settings_row = SiteSettings.objects.filter(pk=1).first()
    if settings_row is None:
        SiteSettings.objects.create(pk=1)
        emit("✓ Site settings created")

    # --- pages + their sections ------------------------------------------
    # Strictly create-if-missing: re-running this (or running it against a
    # database you have already customised) must never overwrite your edits or
    # spawn "-2" duplicates.
    pages = {}
    for spec in PAGE_SEED:
        spec = dict(spec)
        sections = spec.pop("sections", [])
        wanted_slug = spec.pop("slug")

        page = Page.objects.filter(slug=wanted_slug).first()
        if page is None:
            # The slug is the lookup key and we just proved it is free, so it
            # is safe to assign directly - and it must be explicit, because
            # historical models in migrations do not run save().
            page = Page.objects.create(slug=wanted_slug, **spec)
            emit(f"✓ Page: {page.title}")
        else:
            emit(f"· Page: {page.title} (exists, left untouched)")
        pages[page.slug] = page

        for order, section_spec in enumerate(sections):
            section_spec = dict(section_spec)
            items = section_spec.pop("items", [])
            section, created = PageSection.objects.get_or_create(
                page=page,
                title=section_spec["title"],
                defaults={**section_spec, "order": order},
            )
            for i, item in enumerate(items):
                SectionItem.objects.get_or_create(
                    section=section,
                    order=i,
                    defaults=dict(item),
                )

    # --- navigation -------------------------------------------------------
    for order, (position, label, target, icon) in enumerate(NAV_SEED):
        page = pages.get(target)
        NavigationItem.objects.get_or_create(
            label=label,
            position=position,
            defaults={
                "page": page,
                "url": "" if page else target,
                "icon": icon,
                "order": order,
            },
        )
    emit(f"✓ {NavigationItem.objects.count()} navigation links ready")

    # --- socials ----------------------------------------------------------
    for order, (network, url, icon) in enumerate(SOCIAL_SEED):
        SocialLink.objects.get_or_create(
            network=network, defaults={"url": url, "icon": icon, "order": order}
        )
    emit(f"✓ {SocialLink.objects.count()} social links ready")

    # --- small reference data --------------------------------------------
    for i, name in enumerate(EVENT_CATEGORIES):
        category = EventCategory.objects.filter(name=name).first()
        if category is None:
            EventCategory.objects.create(
                name=name, order=i, slug=unique_slug(EventCategory, name)
            )
        elif not category.slug:
            # Legacy row saved before slugs were generated.
            EventCategory.objects.filter(pk=category.pk).update(
                slug=unique_slug(EventCategory, name)
            )

    if not Organiser.objects.exists():
        Organiser.objects.create(
            name="Festival Director",
            role="Overall coordination",
            bio="Add names, roles and photos under Organisers in the admin.",
        )
        Organiser.objects.create(
            name="Technical Lead",
            role="Events & infrastructure",
            bio="Add names, roles and photos under Organisers in the admin.",
        )

    if not Sponsor.objects.exists():
        Sponsor.objects.create(name="Your Sponsor", tier="title")
        Sponsor.objects.create(name="Partner One", tier="gold")
        Sponsor.objects.create(name="Partner Two", tier="silver")

    return pages