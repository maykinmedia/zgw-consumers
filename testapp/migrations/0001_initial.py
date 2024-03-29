# Generated by Django 3.1.4 on 2022-07-19 04:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("zgw_consumers", "0015_auto_20220307_1522"),
    ]

    operations = [
        migrations.CreateModel(
            name="Case",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "_casetype_relative",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                (
                    "_casetype_api",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="zgw_consumers.service",
                    ),
                ),
            ],
        ),
    ]
