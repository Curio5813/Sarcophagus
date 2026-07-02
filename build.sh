#!/bin/sh

echo "Instalando dependências..."
pip install -r requirements.txt

echo "Aplicando migrações do banco de dados..."
python manage.py migrate

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

