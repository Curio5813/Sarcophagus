# Generated by Django 5.1.1 on 2024-10-09 00:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_remove_membro_criado_membro_groups_membro_is_admin_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membro',
            name='senha',
            field=models.CharField(max_length=100, verbose_name='Senha'),
        ),
    ]
