from elasticsearch import Elasticsearch

# Tente conectar ao Elasticsearch na porta padrão
es = Elasticsearch(["http://localhost:9200"])

# Verifique a conexão
if es.ping():
    print("Conexão bem-sucedida com o Elasticsearch!")
else:
    print("Falha na conexão com o Elasticsearch.")
