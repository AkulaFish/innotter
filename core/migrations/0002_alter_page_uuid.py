# Generated by Django 4.1.2 on 2022-11-04 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="page",
            name="uuid",
            field=models.UUIDField(auto_created=True, unique=True),
        ),
    ]
