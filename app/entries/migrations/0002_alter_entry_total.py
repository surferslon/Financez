# Generated by Django 5.0.3 on 2024-03-29 18:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("entries", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="entry",
            name="total",
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=15),
        ),
    ]