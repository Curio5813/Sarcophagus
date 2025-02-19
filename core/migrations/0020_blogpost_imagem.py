# Generated by Django 5.1.1 on 2024-10-16 17:09

import stdimage.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_blogpost_blogcomment'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='imagem',
            field=stdimage.models.StdImageField(default='static/img/games/16.jpg', force_min_size=False, upload_to='blog/', variations={'thumbnail': (700, 400, True)}),
            preserve_default=False,
        ),
    ]
