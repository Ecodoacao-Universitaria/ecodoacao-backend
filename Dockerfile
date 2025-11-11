FROM python:3.11-slim

# Evita que o Python grave arquivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Saída do Python não é bufferizada
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências do sistema necessárias pro PostgreSQL
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o projeto
COPY . .

# Expõe a porta do Django
EXPOSE 8000

# Script de inicialização
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]