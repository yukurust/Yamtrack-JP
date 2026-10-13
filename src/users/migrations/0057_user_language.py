from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0056_user_home_hide_unreleased"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="language",
            field=models.CharField(
                blank=True,
                default="",
                help_text="Interface language. Empty uses the site default.",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="date_format",
            field=models.CharField(
                choices=[
                    ("Y-m-d", "2026-01-18 (ISO)"),
                    ("d/m/Y", "18/01/2026 (EU)"),
                    ("m/d/Y", "01/18/2026 (US)"),
                    ("M j, Y", "Jan 18, 2026"),
                    ("j M, Y", "18 Jan, 2026"),
                    ("Y年n月j日", "2026年1月18日"),
                ],
                default="Y-m-d",
                help_text="Preferred date display format",
                max_length=20,
            ),
        ),
    ]
