from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("sitemap/", views.site_map, name="site_map"),
    path("contact/", views.contact, name="contact"),
    path("register/", views.register, name="register"),
    path("signin/", views.SignInView.as_view(), name="signin"),
    path("signup/", views.signup, name="signup"),
    path("signout/", views.SignOutView.as_view(), name="signout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("events/<slug:slug>/", views.event_detail, name="event_detail"),
    path("workshops/<slug:slug>/", views.workshop_detail, name="workshop_detail"),
    path("competitions/<slug:slug>/", views.competition_detail, name="competition_detail"),
    path("accommodation/<slug:slug>/", views.accommodation_detail, name="accommodation_detail"),
    # Catch-all: every Page row is reachable at a clean URL like /events/ or /ces/.
    # Declared last so the fixed routes above always win.
    path("<slug:slug>/", views.page, name="page"),
]
