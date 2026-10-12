"""
Creates the initial site structure: settings, every page, navigation links,
socials and a few editable example sections.

Safe to re-run -- it only fills in what is missing.

    python manage.py seed_site
    python manage.py seed_site --reset-content   (wipes demo events etc.)
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import (
    Accommodation,
    Competition,
    Event,
    EventCategory,
    NavigationItem,
    Organiser,
    Page,
    PageSection,
    SectionItem,
    SiteSettings,
    SocialLink,
    Sponsor,
    Workshop,
)

PAGE_SEED = [
    {
        "slug": "home",
        "title": "Home",
        "template": Page.Template.HOME,
        "eyebrow": "BIT Durg's",
        "hero_title": "OJUS",
        "meta_left": "16th – 18th December",
        "meta_right": "30th Edition",
        "description": "ASIA'S LARGEST SCIENCE & TECHNOLOGY FESTIVAL",
        "tagline": "— An Aetherial Renaissance —",
        "show_in_header": False,
        "show_in_side_panel": True,
        "order": 0,
        "sections": [
            {
                "title": "What is OJUS",
                "kicker": "The festival",
                "subtitle": "Three days of talks, builds, contests and experiments.",
                "layout": "text",
                "body": (
                    "OJUS is the annual science and technology festival of BIT Durg. "
                    "Replace this paragraph with your own introduction — it lives in the admin "
                    "under Pages › Home › What is OJUS."
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
        "template": Page.Template.EVENTS,
        "eyebrow": "Programme",
        "hero_title": "Events",
        "description": "Keynotes, exhibitions and showcases across all three days.",
        "show_in_header": False,
        "show_in_side_panel": True,
        "order": 1,
        "sections": [
            {
                "title": "Schedule at a glance",
                "kicker": "Timeline",
                "layout": "timeline",
                "body": "",
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
        "template": Page.Template.CES,
        "eyebrow": "Showcase",
        "hero_title": "CES",
        "description": "The OJUS showcase floor — exhibits, demos and product launches.",
        "show_in_side_panel": True,
        "order": 2,
    },
    {
        "slug": "ignite",
        "title": "Ignite",
        "template": Page.Template.IGNITE,
        "eyebrow": "Programme",
        "hero_title": "Ignite",
        "description": "The ignition stage — talks that set the festival in motion.",
        "show_in_header": True,
        "order": 3,
    },
    {
        "slug": "workshops",
        "title": "Workshops",
        "template": Page.Template.WORKSHOPS,
        "eyebrow": "Learn",
        "hero_title": "Workshops",
        "description": "Small-group, hands-on sessions led by faculty and industry mentors.",
        "show_in_header": True,
        "order": 4,
    },
    {
        "slug": "competitions",
        "title": "Competitions",
        "template": Page.Template.COMPETITIONS,
        "eyebrow": "Compete",
        "hero_title": "Competitions",
        "description": "Challenges in hardware, software, design and robotics.",
        "show_in_header": True,
        "order": 5,
    },
    {
        "slug": "accommodation",
        "title": "Accommodation",
        "template": Page.Template.ACCOMMODATION,
        "eyebrow": "Stay",
        "hero_title": "Accommodation",
        "description": "Hostels, hotels and camps near the BIT Durg campus.",
        "show_in_header": True,
        "order": 6,
    },
    {
        "slug": "about",
        "title": "About Us",
        "template": Page.Template.ABOUT,
        "eyebrow": "Who we are",
        "hero_title": "About Us",
        "description": "The student team and the story behind the festival.",
        "show_in_side_panel": True,
        "order": 7,
        "body": (
            "OJUS is run entirely by students of BIT Durg. Replace this text with your "
            "own history, mission and vision — edit it under Pages › About Us."
        ),
    },
    {
        "slug": "contact",
        "title": "Contact Us",
        "template": Page.Template.CONTACT,
        "eyebrow": "Get in touch",
        "hero_title": "Contact Us",
        "description": "Questions, sponsorships, volunteering or anything else.",
        "show_in_side_panel": True,
        "order": 8,
    },
    {
        "slug": "requirements",
        "title": "Requirements",
        "template": Page.Template.REQUIREMENTS,
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
                "body": "",
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

NAV_SEED = [
    # (position, label, slug or url, icon)
    (NavigationItem.Position.HEADER, "Accommodation", "accommodation", ""),
    (NavigationItem.Position.HEADER, "Workshops", "workshops", ""),
    (NavigationItem.Position.HEADER, "Competitions", "competitions", ""),
    (NavigationItem.Position.HEADER, "Ignite", "ignite", ""),
    (NavigationItem.Position.LEFT, "Home", "home", "⌂"),
    (NavigationItem.Position.LEFT, "Events", "events", "▦"),
    (NavigationItem.Position.LEFT, "CES", "ces", "◈"),
    (NavigationItem.Position.LEFT, "Contact Us", "contact", "♧"),
    (NavigationItem.Position.LEFT, "About Us", "about", "ⓘ"),
    (NavigationItem.Position.LEFT, "Requirements", "requirements", "✓"),
    (NavigationItem.Position.FOOTER, "Requirements", "requirements", ""),
    (NavigationItem.Position.FOOTER, "All pages", "/sitemap/", ""),
]

SOCIAL_SEED = [
    (SocialLink.Network.INSTAGRAM, "https://instagram.com", "◎"),
    (SocialLink.Network.X, "https://x.com", "𝕏"),
    (SocialLink.Network.LINKEDIN, "https://linkedin.com", "in"),
    (SocialLink.Network.FACEBOOK, "https://facebook.com", "f"),
    (SocialLink.Network.YOUTUBE, "https://youtube.com", "▶"),
]


class Command(BaseCommand):
    help = "Create the initial OJUS site structure (pages, navigation, settings)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-content",
            action="store_true",
            help="Also delete existing events, workshops, competitions and accommodation.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # Windows consoles default to cp1252 and choke on the ✓ / · glyphs.
        try:
            self.stdout.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

        site = SiteSettings.load()
        self.stdout.write(self.style.SUCCESS(f"✓ Site settings ready ({site.site_name} · {site.organisation})"))

        pages = {}
        for spec in PAGE_SEED:
            sections = spec.pop("sections", [])
            page, created = Page.objects.update_or_create(
                slug=spec["slug"],
                defaults=spec,
            )
            pages[page.slug] = page
            self.stdout.write(f"{'✓' if created else '·'} Page: {page.title} ({page.get_template_display()})")

            for order, sec in enumerate(sections):
                items = sec.pop("items", [])
                section, _ = PageSection.objects.get_or_create(
                    page=page,
                    title=sec["title"],
                    defaults={**sec, "order": order},
                )
                for i, item in enumerate(items):
                    SectionItem.objects.get_or_create(
                        section=section, title=item.get("title", ""), defaults={**item, "order": i}
                    )

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
        self.stdout.write(self.style.SUCCESS(f"✓ {NavigationItem.objects.count()} navigation links ready"))

        for order, (network, url, icon) in enumerate(SOCIAL_SEED):
            SocialLink.objects.get_or_create(
                network=network, defaults={"url": url, "icon": icon, "order": order}
            )
        self.stdout.write(self.style.SUCCESS(f"✓ {SocialLink.objects.count()} social links ready"))

        if options["reset_content"]:
            Event.objects.all().delete()
            Workshop.objects.all().delete()
            Competition.objects.all().delete()
            Accommodation.objects.all().delete()
            self.stdout.write(self.style.WARNING("• Cleared existing content rows"))
            return

        if not EventCategory.objects.exists():
            for i, name in enumerate(["Keynote", "Exhibition", "Workshop", "Performance"]):
                EventCategory.objects.create(name=name, order=i)
            self.stdout.write(self.style.SUCCESS("✓ Event categories ready"))

        if not Organiser.objects.exists():
            Organiser.objects.create(name="Festival Director", role="Overall coordination",
                                     bio="Add names, roles and photos under Organisers in the admin.")
            Organiser.objects.create(name="Technical Lead", role="Events & infrastructure",
                                     bio="Add names, roles and photos under Organisers in the admin.")
            self.stdout.write(self.style.SUCCESS("✓ Organiser placeholders ready"))

        if not Sponsor.objects.exists():
            Sponsor.objects.create(name="Your Sponsor", tier="title")
            Sponsor.objects.create(name="Partner One", tier="gold")
            Sponsor.objects.create(name="Partner Two", tier="silver")
            self.stdout.write(self.style.SUCCESS("✓ Sponsor placeholders ready"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Seed complete. Start the server: python manage.py runserver"))
