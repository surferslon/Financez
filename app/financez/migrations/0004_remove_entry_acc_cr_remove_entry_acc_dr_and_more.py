# Generated by Django 5.0.3 on 2024-03-29 18:06

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("financez", "0003_auto_20200120_1914"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="entry",
            name="acc_cr",
        ),
        migrations.RemoveField(
            model_name="entry",
            name="acc_dr",
        ),
        migrations.RemoveField(
            model_name="accountbalance",
            name="acc",
        ),
        migrations.RemoveField(
            model_name="accountbalance",
            name="currency",
        ),
        migrations.RemoveField(
            model_name="currency",
            name="user",
        ),
        migrations.RemoveField(
            model_name="entry",
            name="currency",
        ),
        migrations.RemoveField(
            model_name="entry",
            name="user",
        ),
        migrations.DeleteModel(
            name="Account",
        ),
        migrations.DeleteModel(
            name="AccountBalance",
        ),
        migrations.DeleteModel(
            name="Currency",
        ),
        migrations.DeleteModel(
            name="Entry",
        ),
    ]