# Generated by Django 3.2.8 on 2021-11-14 18:40

from django.db import migrations
import embed_video.fields


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0037_auto_20211114_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='movies',
            name='video',
            field=embed_video.fields.EmbedVideoField(default=0),
            preserve_default=False,
        ),
    ]
