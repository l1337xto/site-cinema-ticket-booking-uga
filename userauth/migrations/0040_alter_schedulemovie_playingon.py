# Generated by Django 3.2.8 on 2021-11-15 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0039_alter_movies_archived'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedulemovie',
            name='PlayingOn',
            field=models.DateField(db_index=True),
        ),
    ]
