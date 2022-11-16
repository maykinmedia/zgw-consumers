# Generated by Django 3.2.15 on 2022-11-15 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("testapp", "0002_auto_20221115_0738"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="case",
            name="_casetype_api_and__casetype_relative_filled",
        ),
        migrations.AddConstraint(
            model_name="case",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        ("_casetype_api__isnull", True),
                        models.Q(
                            ("_casetype_relative__isnull", True),
                            ("_casetype_relative", ""),
                            _connector="OR",
                        ),
                    ),
                    models.Q(
                        models.Q(("_casetype_api__isnull", True), _negated=True),
                        models.Q(
                            models.Q(
                                ("_casetype_relative__isnull", True),
                                ("_casetype_relative", ""),
                                _connector="OR",
                            ),
                            _negated=True,
                        ),
                    ),
                    _connector="OR",
                ),
                name="testapp_case__casetype_api_and__casetype_relative_filled",
            ),
        ),
    ]
