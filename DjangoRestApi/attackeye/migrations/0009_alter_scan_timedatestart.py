# Generated by Django 4.0.3 on 2022-12-13 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attackeye', '0008_alter_scan_timedatestart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scan',
            name='timeDateStart',
            field=models.DateTimeField(auto_now_add=True, verbose_name='DATE'),
        ),
    ]