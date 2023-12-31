# Generated by Django 4.2.5 on 2023-11-03 12:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="max_storage",
            field=models.PositiveBigIntegerField(
                blank=True, default=1073741824, verbose_name="max storage"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="storage_used",
            field=models.PositiveBigIntegerField(
                blank=True, default=0, verbose_name="storage used"
            ),
        ),
    ]
