# Comment faire pour installer / lancer l'instance

## Installer l'instance
### Cloner le répository

Exécuter la commande `git clone git@github.com:The-independant-project/ouaf.git`

### Build l'image

Dans le répertoire où la solution a été clonée, exécuter la commande `docker build --tag="<nom du tag>" .`

### Créer le fichier .env

Dans le répertoire où la solution a été clonée, copier coller le fichier `.env.exemple` vers un fichier nomme `.env`.
Eventuellement modifier les valeurs à l'intérieur de ce fichier `.env`.
Le fichier .env a pour but de conserver les paramètres de locaux (id, mdp, port...) nécessaires au bon fonctionnement de l'instance docker.

## Lancer l'instance
### Compose l'image

Dans le répertoire où la solution a été clonée, exécuter la commande `docker compose -p <nom de l'image de sortie> -f docker-compose.yml up`
Dans notre cas, cela va également lancer le container.

### Rentrer dans l'image

Dans un nouveau terminal, envoyer une commande pour lancer un shell au container : `docker exec -it <nom du container> bash`
Cela ouvre un shell bash.
Dans ce shell, aller dans le répertire `/app/ouaf` et lancer la commande `python manage.py runserver 0:0:0:0:8000`
Le serveur tournera alors sur l'IP locale de la machine, sur le port 8000.
On peut alors y accéder sur un navigateur, via `localhost:8000`
