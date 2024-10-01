from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import Games


@registry.register_document
class GamesDocument(Document):
    class Index:
        # Nome do índice no Elasticsearch
        name = 'games'

    class Django:
        model = Games  # Modelo que você quer indexar
        fields = [
            'game',
            'descricao',
            'genero',
            'rating',
            'ano',
            'desenvolvedor',
            'distribuidor',
        ]
