# Generated by Django 3.2.8 on 2021-10-28 06:20

from django.db import migrations
import mirage.fields


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0008_user_card_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='card_no',
            field=mirage.fields.EncryptedIntegerField(max_length=64),
        ),
    ]
