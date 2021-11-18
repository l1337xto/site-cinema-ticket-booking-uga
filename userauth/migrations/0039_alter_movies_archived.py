# Generated by Django 3.2.8 on 2021-11-15 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0038_movies_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movies',
            name='archived',
            field=models.BooleanField(blank=True, default=False, help_text='Setting as yes will not allow users to book ticket for this movie', null=True),
        ),
    ]
