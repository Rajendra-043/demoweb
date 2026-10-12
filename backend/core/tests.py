"""Smoke tests: every page and form the site exposes."""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import SignupForm
from .models import (
    Accommodation,
    Competition,
    ContactMessage,
    Event,
    EventCategory,
    NavigationItem,
    Organiser,
    Page,
    Registration,
    SectionItem,
    SiteSettings,
    SocialLink,
    Sponsor,
    Workshop,
)


class SeedTests(TestCase):
    def test_seed_command_is_idempotent(self):
        from django.core.management import call_command

        call_command("seed_site", verbosity=0)
        call_command("seed_site", verbosity=0)
        self.assertEqual(Page.objects.filter(slug="home").count(), 1)
        self.assertGreaterEqual(Page.objects.count(), 9)

    def test_settings_singleton(self):
        SiteSettings.load()
        SiteSettings.load()
        self.assertEqual(SiteSettings.objects.count(), 1)

    def test_navigation_targets_resolve(self):
        for link in NavigationItem.objects.all():
            self.assertTrue(link.target.startswith("/") or link.target.startswith("http"),
                            f"{link} has an unusable target")


class PageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call = __import__("django.core.management", fromlist=["call_command"]).call_command
        call("seed_site", verbosity=0)

        cls.category, _ = EventCategory.objects.get_or_create(name="Keynote")

        cls.event = Event.objects.create(
            title="Opening Keynote",
            summary="The state of research in India.",
            body="Full details go here.",
            category=cls.category,
            start_at=timezone.now() + timedelta(days=30),
            venue="Main Auditorium",
            is_featured=True,
            registration_url="https://example.com",
        )
        cls.workshop = Workshop.objects.create(
            title="Intro to ROS",
            track="Robotics",
            instructor="Dr. Rao",
            summary="Build a robot in two days.",
            date=(timezone.now() + timedelta(days=10)).date(),
            venue="Lab 3",
            seats=30,
            price="500",
            is_featured=True,
        )
        cls.competition = Competition.objects.create(
            title="Line Follower",
            category="Robotics",
            summary="Fastest wins.",
            prize="Rs 50,000",
            deadline=(timezone.now() + timedelta(days=20)).date(),
            team_size="2-4",
            is_featured=True,
        )
        cls.stay = Accommodation.objects.create(
            name="Campus Hostel A",
            summary="On campus rooms.",
            distance_from_campus="0.3 km",
            price_per_night="800",
            capacity=120,
            amenities="Wi-Fi, Meals, Laundry",
        )
        cls.organiser = Organiser.objects.create(name="Festival Director", role="Coordination")
        cls.sponsor = Sponsor.objects.create(name="Acme Corp", tier="title")

    # ---- pages -------------------------------------------------------------

    def test_home_page(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OJUS")
        self.assertContains(response, "background.jpg")

    def test_every_seeded_page_renders(self):
        for page in Page.objects.filter(is_published=True):
            with self.subTest(page=page.slug):
                response = self.client.get(page.get_absolute_url())
                self.assertEqual(response.status_code, 200)

    def test_detail_pages(self):
        for obj in (self.event, self.workshop, self.competition, self.stay):
            with self.subTest(obj=obj):
                response = self.client.get(obj.get_absolute_url())
                self.assertEqual(response.status_code, 200)

    def test_unpublished_page_returns_404(self):
        Page.objects.filter(slug="ces").update(is_published=False)
        response = self.client.get("/ces/")
        self.assertEqual(response.status_code, 404)

    def test_unpublished_content_returns_404(self):
        self.event.is_published = False
        self.event.save()
        self.assertEqual(self.client.get(self.event.get_absolute_url()).status_code, 404)

    def test_static_pages(self):
        for name in ("search", "site_map", "signin", "signup", "contact"):
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(f"core:{name}")).status_code, 200)

    def test_admin_reachable(self):
        self.assertEqual(self.client.get("/admin/").status_code, 302)  # redirects to login

    # ---- placeholders ------------------------------------------------------

    def test_empty_section_renders_placeholder(self):
        """An empty PageSection must still show a labelled content space."""
        page = Page.objects.get(slug="ces")
        section = page.sections.create(title="Exhibit Wall", layout="cards")
        response = self.client.get(page.get_absolute_url())
        self.assertContains(response, "Exhibit Wall")
        self.assertContains(response, "No cards yet")

    def test_section_with_body_does_not_show_placeholder(self):
        """A text section that already has copy must not claim to be empty."""
        page = Page.objects.get(slug="ces")
        page.sections.create(title="Intro", layout="text", body="Some real copy.")
        response = self.client.get(page.get_absolute_url())
        self.assertContains(response, "Some real copy.")
        self.assertNotContains(response, "This block is empty")

    def test_section_items_render(self):
        page = Page.objects.get(slug="ces")
        section = page.sections.create(title="Tracks", layout="cards", columns=3)
        SectionItem.objects.create(section=section, title="Aerospace", icon="✈")
        response = self.client.get(page.get_absolute_url())
        self.assertContains(response, "Aerospace")

    def test_empty_listing_page_shows_hint(self):
        Event.objects.all().delete()
        response = self.client.get("/events/")
        self.assertContains(response, "No events have been published yet")

    # ---- forms -------------------------------------------------------------

    def test_contact_form_creates_message(self):
        before = ContactMessage.objects.count()
        response = self.client.post(
            reverse("core:contact"),
            {
                "name": "Tester",
                "email": "t@example.com",
                "subject": "Hello",
                "message": "This is a sufficiently long test message.",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), before + 1)

    def test_contact_form_rejects_short_message(self):
        before = ContactMessage.objects.count()
        self.client.post(
            reverse("core:contact"),
            {"name": "Tester", "email": "t@example.com", "subject": "x", "message": "hi"},
        )
        self.assertEqual(ContactMessage.objects.count(), before)

    def test_signup_then_signin(self):
        response = self.client.post(
            reverse("core:signup"),
            {
                "first_name": "Asha",
                "last_name": "R",
                "email": "asha@example.com",
                "username": "asha",
                "password1": "Str0ngPass!2026",
                "password2": "Str0ngPass!2026",
            },
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("core:register"),
            {"full_name": "Asha R", "email": "asha@example.com", "interest": "workshop", "college": "BIT Durg"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Registration.objects.count(), 1)

        self.client.post(reverse("core:signout"))
        response = self.client.get(reverse("core:dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_signup_password_mismatch(self):
        form = SignupForm(
            {
                "first_name": "A",
                "email": "b@example.com",
                "username": "b",
                "password1": "Str0ngPass!2026",
                "password2": "different",
            }
        )
        self.assertFalse(form.is_valid())

    def test_search(self):
        response = self.client.get(reverse("core:search"), {"q": "Keynote"})
        self.assertContains(response, "Opening Keynote")

    def test_social_links_render_in_footer(self):
        SocialLink.objects.get_or_create(network="instagram", defaults={"url": "https://instagram.com", "icon": "◎"})
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "instagram.com")

    def test_requirements_page(self):
        page = Page.objects.get(slug="requirements")
        self.assertEqual(page.template, Page.Template.REQUIREMENTS)
        response = self.client.get("/requirements/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Who can participate")
        self.assertContains(response, "Documents to carry")

    def test_checklist_layout_renders(self):
        page = Page.objects.get(slug="requirements")
        section = page.sections.create(title="Kit to carry", layout="checklist")
        SectionItem.objects.create(section=section, title="Power bank", icon="⚡",
                                   body="The halls have limited charging points.")
        response = self.client.get("/requirements/")
        self.assertContains(response, "checklist-item")
        self.assertContains(response, "Power bank")
        self.assertContains(response, "⚡")

    def test_requirements_reachable_from_side_panel(self):
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, 'href="/requirements/"')

    def test_right_side_panel_is_populated(self):
        """The floating right panel must never be an empty shell."""
        response = self.client.get(reverse("core:home"))
        self.assertContains(response, "side-panel right-panel")
        self.assertContains(response, 'aria-label="Instagram"')
