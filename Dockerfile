# Utiliser une image de base Python
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LANG=fr_FR.UTF-8 \
    LC_ALL=fr_FR.UTF-8 \
    PIP_NO_CACHE_DIR=1

# Définir le répertoire de travail à l'intérieur du conteneur
WORKDIR /app

# Installer les packages système nécessaires (incluant nano)
RUN apt-get update && apt-get install -y \
    nano \
    gcc \
    gettext \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*




# Copier le fichier de dépendances requirements.txt
COPY requirements.txt /app/

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application dans le conteneur
COPY . /app/

RUN python manage.py collectstatic --noinput || true
RUN python manage.py compilemessages || true

RUN chmod -R 777 /app

# Exposer le port sur lequel Django sera disponible
EXPOSE 8080

# Commande pour démarrer le serveur Django
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

CMD ["tail", "-f", "/dev/null"]
