# Generated by Django 3.0 on 2019-12-23 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financez', '0004_auto_20191223_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='code',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]