# Generated by Django 3.2.8 on 2021-11-09 16:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0025_alter_promotions_promo_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotions',
            name='is_promo_sent',
            field=models.BooleanField(default=False),
        ),
    ]
