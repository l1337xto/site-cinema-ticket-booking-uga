# Generated by Django 3.2.8 on 2021-10-22 02:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0003_auto_20211022_0159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shows',
            name='playing_at',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='userauth.showroom'),
        ),
    ]
