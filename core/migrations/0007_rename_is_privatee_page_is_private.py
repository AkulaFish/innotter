# Generated by Django 4.1.2 on 2022-11-04 11:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_remove_page_is_private_page_is_privatee'),
    ]

    operations = [
        migrations.RenameField(
            model_name='page',
            old_name='is_privatee',
            new_name='is_private',
        ),
    ]