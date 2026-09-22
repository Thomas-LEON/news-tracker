
FROM python:3.12-slim

WORKDIR /app

# Installation des dependances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY src/ /app/src/

# Les dossiers de sortie seront montes via docker-compose (volumes)
CMD ["python", "-u", "src/news_tracker.py"]

