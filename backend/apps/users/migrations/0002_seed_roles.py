from django.db import migrations


def seed_roles(apps, schema_editor):
    Role = apps.get_model("users", "Role")
    codes = ["author", "reviewer", "chief_editor", "tech_editor"]
    for code in codes:
        Role.objects.get_or_create(code=code)


def unseed_roles(apps, schema_editor):
    Role = apps.get_model("users", "Role")
    Role.objects.filter(code__in=["author", "reviewer", "chief_editor", "tech_editor"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_roles, unseed_roles),
    ]
