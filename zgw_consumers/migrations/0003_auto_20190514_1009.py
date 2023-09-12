# Generated by Django 2.2.1 on 2019-05-14 08:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("zgw_consumers", "0002_auto_20190514_0944")]

    operations = [
        migrations.AlterField(
            model_name="service",
            name="api_type",
            field=models.CharField(
                choices=[
                    ("ac", "AC (Authorizations)"),
                    ("nrc", "NRC (Notifications)"),
                    ("zrc", "ZRC (Zaken)"),
                    ("ztc", "ZTC (Zaaktypen)"),
                    ("drc", "DRC (Informatieobjecten)"),
                    ("brc", "BRC (Besluiten)"),
                    ("orc", "ORC (Overige)"),
                ],
                max_length=20,
                verbose_name="type",
            ),
        )
    ]
