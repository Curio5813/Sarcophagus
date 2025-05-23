# Generated by Django 5.1.6 on 2025-05-05 16:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0058_seguir'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mensagem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conteudo', models.TextField()),
                ('enviada_em', models.DateTimeField(auto_now_add=True)),
                ('lida', models.BooleanField(default=False)),
                ('destinatario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensagens_recebidas', to=settings.AUTH_USER_MODEL)),
                ('remetente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mensagens_enviadas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-enviada_em'],
            },
        ),
    ]
