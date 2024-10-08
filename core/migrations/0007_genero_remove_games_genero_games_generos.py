# Generated by Django 5.1.1 on 2024-10-07 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_games_video'),
    ]

    operations = [
        migrations.CreateModel(
            name='Genero',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(choices=[('Action', 'Action'), ('Adventure', 'Adventure'), ('Puzzle', 'Puzzle'), ('Racing', 'Racing'), ('RPG', 'RPG'), ('Shooter', 'Shooter'), ('Simulation', 'Simulation'), ('Sports', 'Sports'), ('Strategy', 'Strategy')], max_length=100, unique=True, verbose_name='Nome')),
            ],
            options={
                'verbose_name': 'Gênero',
                'verbose_name_plural': 'Gêneros',
            },
        ),
        migrations.RemoveField(
            model_name='games',
            name='genero',
        ),
        migrations.AddField(
            model_name='games',
            name='generos',
            field=models.ManyToManyField(to='core.genero', verbose_name='Gêneros'),
        ),
    ]
