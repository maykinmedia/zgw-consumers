# Generated by Django 2.2.10 on 2020-03-31 14:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("zgw_consumers", "0007_service_nlx"),
    ]

    operations = [
        migrations.AlterField(
            model_name="service",
            name="auth_type",
            field=models.CharField(
                choices=[
                    ("no_auth", "No authorization"),
                    ("api_key", "API key"),
                    ("zgw", "ZGW client_id + secret"),
                ],
                default="zgw",
                max_length=20,
                verbose_name="authorization type",
            ),
        ),
        migrations.AlterField(
            model_name="service",
            name="nlx",
            field=models.URLField(
                blank=True,
                help_text="NLX (outway) address",
                max_length=1000,
                verbose_name="NLX url",
            ),
        ),
        migrations.AlterField(
            model_name="service",
            name="oas",
            field=models.URLField(
                help_text="URL to OAS yaml file", max_length=1000, verbose_name="OAS"
            ),
        ),
    ]
