# Generated by Django 5.1.6 on 2025-04-30 17:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0056_rename_lida_notificacao_visualizada'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notificacao',
            old_name='visualizada',
            new_name='lida',
        ),
    ]
