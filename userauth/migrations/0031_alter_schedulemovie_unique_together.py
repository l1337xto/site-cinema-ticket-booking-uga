# Generated by Django 3.2.8 on 2021-11-11 14:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0030_auto_20211111_1458'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='schedulemovie',
            unique_together={('showroom', 'movietime1')},
        ),
    ]
