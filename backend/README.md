# OJUS — Django site

Backend for the OJUS festival site, built from the original cinematic glass
HTML design in `../fontend/page/index.html`.

Organisation: **BIT Durg**. Fest: **OJUS**.

---

## Run it

```powershell
cd backend
python manage.py migrate
python manage.py seed_site
python manage.py createsuperuser
python manage.py runserver
```

| URL | What it is |
|---|---|
| <http://127.0.0.1:8000/> | Home (full-screen hero) |
| <http://127.0.0.1:8000/admin/> | **All content is edited here** |
| `/events/` `/ces/` `/ignite/` | Event pages |
| `/workshops/` `/competitions/` `/accommodation/` | Programme pages |
| `/about/` `/contact/` | Info + working contact form |
| `/requirements/` | Eligibility, documents to carry, ground rules |
| `/signin/` `/signup/` `/dashboard/` | Accounts |

Run the tests with `python manage.py test core` (24 tests).

---

## How the "empty but ready" pages work

Every page is a `Page` row. Under it you add `PageSection` blocks, and inside
each section you add `SectionItem` cards. Three behaviours make the page usable
before you have written anything:

1. **A section with no content still renders.** It shows a dashed
   *"Content space — this block is empty"* panel with your section title, so you
   can see where copy will go. See `templates/core/includes/sections.html`.
2. **A listing page with no records still renders.** Events / Workshops /
   Competitions / Accommodation show *"No events have been published yet"* plus
   a button straight to the matching admin add-form.
3. **A page with no sections at all** shows a single line pointing at its admin
   edit URL.

Section layouts available: `text`, `cards`, `featured`, `gallery`, `timeline`,
`stats`, `checklist`, `cta` — pick one in the admin and the template switches.
`checklist` is what the Requirements page uses for its tick-off rows.

---

## Editing guide

| To change… | Go to… |
|---|---|
| Logo, hero text, background image, trailer, footer, contact details | **Site settings** (single row) |
| Navbar + left/right side panels + footer links | **Navigation links** |
| The 5 social icons in the right panel | **Social links** |
| Page hero copy and content blocks | **Pages** → open the page → *Page sections* inline |
| Cards inside a block | **Page sections** → open the section → *Section items* |
| Events / Workshops / Competitions / Accommodation | their own menus |
| **Eligibility rules, ID requirements, code of conduct** | **Pages → Requirements** |
| Team, sponsors, FAQ | **Organisers**, **Sponsors**, **FAQs** |
| Messages sent via the contact form | **Contact messages** (has a *mark handled* action) |
| Attendee sign-ups | **Registrations** |

### Changing the hero background

Two ways:

* **Upload** — *Site settings → Background image*. Overrides the bundled file.
* **Replace the file** — drop your photo at
  `backend/static/img/background.jpg`.

The original photo is also at `fontend/page/background.jpg` for the standalone
HTML mock-up.

The photo is a bright daytime shot, so `static/css/site.css` layers a heavy
dark scrim over it (`.hero`) to keep the glass UI readable. To lighten it, lower
the alpha values in that rule.

---

## Layout

```
backend/
  ojus/                 project settings, root urls
  core/
    models.py           SiteSettings, Page, PageSection, SectionItem,
                        Event, Workshop, Competition, Accommodation,
                        Organiser, Sponsor, FAQ, ContactMessage, Registration
    views.py            home, generic page dispatcher, details, forms, auth
    admin.py            full editing UI
    context_processors.py  injects site settings + navigation into every page
    forms.py            contact, registration, signup
    urls.py             all routes (namespace "core")
    tests.py            19 smoke tests
    management/commands/seed_site.py
  templates/
    base.html           the hero design: header, side panels, footer, modal
    core/               one template per page type + shared includes
  static/css/site.css   the full design system
  static/img/background.jpg
fontend/page/index.html  original standalone mock-up (OJUS branding, same photo)
```

### Adding a new page

1. **Pages → Add**. Give it a title and slug; choose a *Template*.
2. Set the hero copy.
3. Add *Page sections* inline. Leave one empty if you don't have copy yet.
4. Tick **Show in header** / **Show in side panel**, or add a
   **Navigation link** pointing at it.

`/your-slug/` goes live immediately. Untick **Published** to hide it.

### Adding a whole new section layout

Add a choice to `PageSection.Layout`, then add a branch in
`templates/core/includes/sections.html`.

---

## Notes

* SQLite by default. For Postgres set `DATABASES` in `ojus/settings.py`.
* `DEBUG=1` and `ALLOWED_HOSTS` come from env vars:
  `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_SECRET_KEY`,
  `DJANGO_CSRF_TRUSTED_ORIGINS`.
* Uploaded media goes to `backend/media/`.
* Email is printed to the console in development
  (`EMAIL_BACKEND = console`), so nothing is sent from localhost.
* Before deploying: set a real `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, run
  `python manage.py collectstatic`, and serve with a real WSGI server.
