# Generated by Django 4.1.2 on 2022-11-04 10:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0004_alter_page_follow_requests'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='follow_requests',
            field=models.ManyToManyField(default=[], related_name='requests', to=settings.AUTH_USER_MODEL),
        ),
    ]