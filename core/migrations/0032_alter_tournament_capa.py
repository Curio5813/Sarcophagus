# Generated by Django 5.1.1 on 2024-11-25 17:58

import stdimage.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_alter_tournament_capa'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='capa',
            field=stdimage.models.StdImageField(blank=True, force_min_size=False, null=True, upload_to='tournaments/capas', variations={'thumb': {'height': 578, 'width': 400}}, verbose_name='Capa do Campeonato'),
        ),
    ]
