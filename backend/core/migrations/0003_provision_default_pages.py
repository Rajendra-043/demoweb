"""
Provisions the default site structure on every database that gets migrated.

Why this exists
---------------
The whole site is driven by database rows (Page, NavigationItem, SocialLink...).
On a fresh deployment -- a new Render dyno, a new container, a rebuilt CI
database -- there are no rows, so ``core.views.home`` raised
``Page.DoesNotExist`` and every URL returned 404.

Running this as a data migration means ``manage.py migrate`` alone is enough
to bring a brand new database up to a working state, with no extra manual step.

Safe to re-run and safe on an existing database: everything is
update_or_create / get_or_create keyed on natural identifiers (slug, label,
network), so it never duplicates or overwrites content you have customised.
"""

from django.db import migrations

from core import seeding


def forwards(apps, schema_editor):
    seeding.provision_site(apps=apps)


def backwards(apps, schema_editor):
    """
    Intentionally does nothing.

    Removing the default pages on reverse would delete content an editor may
    have written into them, so this migration only ever goes one way.
    """


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_alter_navigationitem_icon_alter_page_template_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]