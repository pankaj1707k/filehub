# Generated by Django 4.2.5 on 2023-10-12 18:57

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("files", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="directory",
            options={"verbose_name_plural": "directories"},
        ),
    ]