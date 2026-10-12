from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ContactForm, RegistrationForm, SignupForm
from .models import (
    Accommodation,
    Competition,
    Event,
    FAQ,
    Organiser,
    Page,
    PageSection,
    Registration,
    SiteSettings,
    Sponsor,
    Workshop,
)


def _published(queryset):
    return queryset.filter(is_published=True)


def _paginate(request, queryset, per_page=9):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


def home(request):
    """
    Home page.

    The home Page row drives the hero copy, but the page must survive a
    database that has not been provisioned yet (fresh deploy, cleared DB).
    If the row is missing we render the same template with no sections and let
    the SiteSettings defaults supply the hero, so the site degrades to a
    readable landing page instead of a 404.
    """
    page = Page.objects.filter(slug="home").first()
    context = {
        "page": page,
        "sections": page.sections.filter(is_visible=True) if page else PageSection.objects.none(),
        "featured_events": _published(Event.objects.filter(is_featured=True))[:3],
        "upcoming_events": Event.objects.filter(is_published=True).order_by("start_at")[:3],
        "featured_workshops": _published(Workshop.objects.filter(is_featured=True))[:3],
        "featured_competitions": _published(Competition.objects.filter(is_featured=True))[:3],
        "sponsors": _published(Sponsor.objects.all()),
        "needs_provisioning": page is None,
    }
    return render(request, "core/home.html", context)


def page(request, slug):
    page_obj = get_object_or_404(Page, slug=slug, is_published=True)
    sections = page_obj.sections.filter(is_visible=True)
    context = {
        "page": page_obj,
        "sections": sections,
        "faqs": page_obj.faqs.filter(is_visible=True),
    }
    template = {
        Page.Template.HOME: "core/home.html",
        Page.Template.EVENTS: "core/events.html",
        Page.Template.CES: "core/ces.html",
        Page.Template.ABOUT: "core/about.html",
        Page.Template.CONTACT: "core/contact.html",
        Page.Template.ACCOMMODATION: "core/accommodation.html",
        Page.Template.WORKSHOPS: "core/workshops.html",
        Page.Template.COMPETITIONS: "core/competitions.html",
        Page.Template.IGNITE: "core/ignite.html",
        Page.Template.REQUIREMENTS: "core/requirements.html",
    }.get(page_obj.template, "core/page.html")

    if page_obj.template == Page.Template.HOME:
        context.update(
            {
                "featured_events": _published(Event.objects.filter(is_featured=True))[:3],
                "upcoming_events": Event.objects.filter(is_published=True).order_by("start_at")[:3],
                "featured_workshops": _published(Workshop.objects.filter(is_featured=True))[:3],
                "featured_competitions": _published(Competition.objects.filter(is_featured=True))[:3],
                "sponsors": _published(Sponsor.objects.all()),
            }
        )
    elif page_obj.template == Page.Template.EVENTS:
        context.update({"events": _paginate(request, _published(Event.objects.all())), "event_form": ContactForm()})
    elif page_obj.template == Page.Template.WORKSHOPS:
        context.update({"workshops": _paginate(request, _published(Workshop.objects.all())), "event_form": ContactForm()})
    elif page_obj.template == Page.Template.COMPETITIONS:
        context.update({"competitions": _paginate(request, _published(Competition.objects.all())), "event_form": ContactForm()})
    elif page_obj.template == Page.Template.ACCOMMODATION:
        context.update({"stays": _paginate(request, _published(Accommodation.objects.all())), "event_form": ContactForm()})
    elif page_obj.template == Page.Template.ABOUT:
        context.update({"organisers": Organiser.objects.filter(is_visible=True), "sponsors": _published(Sponsor.objects.all()), "faqs": FAQ.objects.filter(is_visible=True)[:8]})
    elif page_obj.template == Page.Template.CONTACT:
        context.update({"event_form": ContactForm()})
    elif page_obj.template == Page.Template.CES:
        context.update({"events": _published(Event.objects.all())[:6]})
    elif page_obj.template == Page.Template.IGNITE:
        context.update({"events": _published(Event.objects.all())[:6]})

    return render(request, template, context)


# ---------------------------------------------------------------------------
# Detail views
# ---------------------------------------------------------------------------


def _detail_context(obj, related):
    """Shared context for the detail templates."""
    cta_url = getattr(obj, "registration_url", "") or getattr(obj, "booking_url", "")
    return {
        "object": obj,
        "related": related,
        "cta_url": cta_url,
        "cta_label": "BOOK NOW" if getattr(obj, "booking_url", "") else "REGISTER",
    }


def event_detail(request, slug):
    obj = get_object_or_404(Event, slug=slug, is_published=True)
    related = Event.objects.filter(is_published=True).exclude(pk=obj.pk)[:3]
    return render(request, "core/event_detail.html", _detail_context(obj, related))


def workshop_detail(request, slug):
    obj = get_object_or_404(Workshop, slug=slug, is_published=True)
    related = Workshop.objects.filter(is_published=True).exclude(pk=obj.pk)[:3]
    return render(request, "core/workshop_detail.html", _detail_context(obj, related))


def competition_detail(request, slug):
    obj = get_object_or_404(Competition, slug=slug, is_published=True)
    related = Competition.objects.filter(is_published=True).exclude(pk=obj.pk)[:3]
    return render(request, "core/competition_detail.html", _detail_context(obj, related))


def accommodation_detail(request, slug):
    obj = get_object_or_404(Accommodation, slug=slug, is_published=True)
    related = Accommodation.objects.filter(is_published=True).exclude(pk=obj.pk)[:3]
    return render(request, "core/accommodation_detail.html", _detail_context(obj, related))


# ---------------------------------------------------------------------------
# Contact / registration
# ---------------------------------------------------------------------------


def contact(request):
    page_obj = Page.objects.filter(slug="contact", is_published=True).first()
    form = ContactForm(request.POST or None)
    sent = False
    if request.method == "POST":
        if form.is_valid():
            message = form.save(commit=False)
            message.page = page_obj
            message.save()
            messages.success(request, "Thanks! Your message has reached the team.")
            form = ContactForm()
            sent = True
    return render(
        request,
        "core/contact.html",
        {"page": page_obj, "sections": page_obj.sections.filter(is_visible=True) if page_obj else [], "event_form": form, "sent": sent},
    )


@require_POST
def register(request):
    form = RegistrationForm(request.POST)
    if form.is_valid():
        reg = form.save(commit=False)
        reg.user = request.user if request.user.is_authenticated else None
        reg.save()
        messages.success(request, "Registration received. See you at Techfest!")
        return redirect(request.POST.get("next") or "core:home")
    messages.error(request, "Please correct the errors in the registration form.")
    return redirect(request.POST.get("next") or "core:home")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class SignInView(LoginView):
    template_name = "core/auth/signin.html"
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # django.contrib.auth.views.LoginView injects its own "site" (a
        # django.contrib.sites RequestSite). Our SiteSettings model is also
        # called "site" and is what the templates expect, so put it back.
        context["site"] = SiteSettings.load()
        context["signup_form"] = SignupForm()
        return context


class SignOutView(LogoutView):
    http_method_names = ["get", "post", "options"]

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


def signup(request):
    if request.user.is_authenticated:
        return redirect("core:home")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome, {user.first_name or user.username}!")
        return redirect("core:dashboard")
    return render(request, "core/auth/signup.html", {"form": form})


@login_required
def dashboard(request):
    registrations = request.user.registrations.all()
    return render(request, "core/dashboard.html", {"registrations": registrations})


def site_map(request):
    pages = Page.objects.filter(is_published=True, allow_in_site_map=True)
    return render(request, "core/sitemap.html", {"pages": pages})


def search(request):
    query = request.GET.get("q", "").strip()
    results = {"events": [], "workshops": [], "competitions": [], "stays": [], "pages": []}
    if query:
        results["events"] = Event.objects.filter(is_published=True).filter(
            Q(title__icontains=query) | Q(summary__icontains=query)
        )[:20]
        results["workshops"] = Workshop.objects.filter(is_published=True).filter(
            Q(title__icontains=query) | Q(track__icontains=query)
        )[:20]
        results["competitions"] = Competition.objects.filter(is_published=True).filter(
            Q(title__icontains=query) | Q(category__icontains=query)
        )[:20]
        results["stays"] = Accommodation.objects.filter(is_published=True).filter(
            Q(name__icontains=query) | Q(kind__icontains=query)
        )[:20]
        results["pages"] = Page.objects.filter(is_published=True).filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:20]
    return render(
        request,
        "core/search.html",
        {
            "query": query,
            "results": results,
            "grouped": [
                ("Events", results["events"]),
                ("Workshops", results["workshops"]),
                ("Competitions", results["competitions"]),
                ("Accommodation", results["stays"]),
            ],
        },
    )
