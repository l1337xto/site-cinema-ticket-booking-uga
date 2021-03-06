# Generated by Django 3.2.8 on 2021-11-09 00:54

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0021_auto_20211109_0052'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedulemovie',
            name='PlayingTill',
            field=models.DateField(blank=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='schedulemovie',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]
