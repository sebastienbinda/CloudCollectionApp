<!--
    ____ _                 _  ____      _ _           _   _             ___
   / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
  | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
  | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
   \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
                                                                             |_|   |_|
  Projet : CloudCollectionApp
  Date de creation : 2026-05-03
  Auteurs : Codex et Binda Sébastien
-->
# CloudCollectionApp

> **Note IA**  
> Le code de ce projet a ete genere et modifie avec l'aide de **Codex**, l'agent de developpement d'**OpenAI** base sur **GPT-5**.

Application web personnelle pour consulter, rechercher et maintenir une collection
de jeux video stockee dans un fichier LibreOffice Calc `.ods`.

Le projet transforme un fichier ODS existant en interface web : tableau de bord,
statistiques par plateforme, recherche globale, consultation par onglet,
liste de souhaits, administration et formulaires d'ajout ou de modification.

## Objectif

L'objectif est de garder le fichier ODS comme source de verite tout en offrant une interface plus confortable pour :

- visualiser les statistiques de l'onglet `Accueil`
- naviguer dans la collection par plateforme
- filtrer les jeux par colonnes
- rechercher un jeu par nom sur toutes les plateformes
- ajouter un jeu dans le bon onglet du fichier ODS en conservant le style existant
- suivre les jeux de la liste de souhaits
- modifier ou supprimer des lignes existantes apres authentification
- preparer les futures fonctionnalites stockees en base PostgreSQL

## Fonctionnalites

- Page d'accueil avec statistiques globales issues de l'onglet `Accueil`
- Cartes plateformes avec image de fond extraite depuis chaque onglet ODS
- Recherche globale par nom de jeu, toutes plateformes confondues
- Page plateforme accessible directement par URL, par exemple `/?platform=Switch`
- Tableau filtrable par colonne, avec filtres specifiques pour les dates et studios
- Bandeau plateforme avec image, nombre de jeux, valeur, prix moyen et nombre de studios
- Page `/wishlist` avec tri par plateforme puis nom du jeu
- Page `/add-game` avec formulaire d'ajout vers la collection ou la liste de souhaits
- Suggestions de valeurs fusionnees entre collection et liste de souhaits, triees alphabetiquement
- Validation backend des champs avant ajout ou modification
- Modification et suppression des jeux de collection ou de liste de souhaits
- Tableau de bord administrateur avec telechargement ODS et reinitialisation du cache
- Page About publique pour les visiteurs non connectes
- Authentification Bearer pour toutes les routes backend sauf `POST /auth/token`
- Barres de progression pendant les chargements et actions longues
- Ecriture backend dans le fichier ODS avec sauvegarde automatique avant modification
- Pipeline GitHub Actions avec tests, build frontend et publication des images Docker

## Architecture Technique

Le projet est separe en deux applications :

- `backend/` : API Python Flask
- `frontend/` : application React construite avec Vite

Le frontend communique avec le backend via les routes `/collections/...`. En developpement, Vite proxifie ces routes vers Flask grace a `frontend/vite.config.js`.

### Backend

Technologies :

- Python 3.12
- Flask
- Flask-Cors
- pandas
- odfpy
- `zipfile` et `xml.etree.ElementTree` pour lire et modifier le contenu ODS

Fichiers principaux :

- `backend/app.py` : routes HTTP Flask
- `backend/services/games/games_service.py` : orchestration de la collection jeux video
- `backend/services/games/add_game_choice_service.py` : fusion et tri des choix du formulaire d'ajout
- `backend/services/ods/` : lecture, ecriture, sauvegarde et validation du fichier ODS
- `backend/services/auth/` : emission et validation des tokens Bearer
- `backend/services/validation/` : validation des payloads collection et liste de souhaits
- `backend/models/jeu_video.py` : normalisation des lignes de jeux video
- `backend/models/collection_types.py` : types de collections supportes

Le service `GamesService` lit les donnees dans le fichier ODS. Pour les
onglets de plateformes, les colonnes de jeux sont lues dans la plage logique
`F:M`, avec la ligne d'en-tete a l'index 5.

Pour chaque ecriture dans le fichier ODS, le backend :

- cree une sauvegarde du fichier ODS original
- ouvre le fichier ODS comme archive ZIP
- modifie `content.xml`
- trouve l'onglet cible, plateforme ou `Liste de souhaits`
- clone ou remplace les cellules en conservant les styles existants
- reecrit le fichier ODS
- invalide le cache de lecture

### Frontend

Technologies :

- React
- Vite
- CSS classique dans `frontend/src/styles.css`

Fichiers principaux :

- `frontend/src/App.jsx` : application React, navigation, pages et appels API
- `frontend/src/components/` : vues, dialogues et composants reutilisables
- `frontend/src/services/` : clients API et services frontend
- `frontend/src/hooks/` : logique React partagee pour auth, mutations et telechargement
- `frontend/src/styles.css` et `frontend/src/styles/` : styles de l'interface
- `frontend/vite.config.js` : configuration Vite et proxy backend

L'application gere les vues principales suivantes :

- about publique
- accueil
- detail d'une plateforme
- liste de souhaits
- ajout d'un jeu
- authentification
- administration

La navigation reste volontairement simple et utilise l'URL :

- `/` : redirection fonctionnelle vers `/about` sans token et `/accueil` avec token
- `/about` : page publique non connectee
- `/accueil` : accueil authentifie
- `/?platform=Playstation%204` : vue d'une plateforme authentifiee
- `/wishlist` : liste de souhaits authentifiee
- `/add-game` : formulaire d'ajout
- `/auth` : authentification
- `/admin-dashboard` : administration

Sans token local, les pages applicatives hors `/about` et `/auth` redirigent vers
la page About.

## Fichier ODS

Le backend ne depend d'aucun fichier ODS code en dur. Le chemin du fichier doit
etre fourni par configuration :

- `JEUXVIDEO_ODS_PATH` pour le backend lance directement
- `JEUXVIDEO_ODS_FILE` pour le montage Docker Compose

Un fichier exemple versionnable est fourni :

- `collection-example.ods`

Il peut etre regenere avec :

```bash
backend/.venv/bin/python scripts/generate_collection_example.py
```

Il est aussi possible de forcer le chemin avec la variable :

```bash
export JEUXVIDEO_ODS_PATH=/chemin/vers/collection.ods
```

Variables utiles pour l'ecriture :

```bash
export JEUXVIDEO_ODS_TMP_DIR=/chemin/temporaire
export JEUXVIDEO_ODS_BACKUP_DIR=/chemin/backup
export ODS_FORMULA_RECALCULATION=required
```

Dans Docker, les fichiers temporaires sont places dans un `tmpfs` et les
sauvegardes dans un montage dedie afin de ne pas devoir monter tout le dossier
parent de la collection.

Structure attendue :

- onglet `Accueil` : statistiques par plateforme
- onglet `Liste de souhaits` : suivi des jeux souhaites ou precommandes
- un onglet par plateforme : `Playstation`, `Playstation 4`, `Switch`, etc.

Les images affichees dans l'interface sont extraites directement des images embarquees dans les onglets du fichier ODS.

## API Principale

### Authentification

Tous les endpoints backend applicatifs exigent un token Bearer OAuth2, sauf les
routes publiques d'authentification et d'inscription :

```http
POST /auth/token
Content-Type: application/json
```

Exemple :

```json
{
  "username": "admin",
  "password": "change-me"
}
```

Configurer les valeurs avec `AUTH_USERNAME`, `AUTH_PASSWORD_ENCRYPTED`,
`AUTH_SECRET_KEY_ENCRYPTED`, `AUTH_ENV_ENCRYPTION_KEY` et `AUTH_TOKEN_TTL_SECONDS`.
Les anciennes variables `AUTH_PASSWORD` et `AUTH_SECRET_KEY` restent acceptees
en secours local, mais le fichier `.env` doit utiliser les valeurs chiffrees.

Generer un nouveau mot de passe, une nouvelle cle HMAC, un mot de passe
PostgreSQL et leurs valeurs chiffrees :

```bash
backend/.venv/bin/python scripts/generate_auth_env.py
```

Reporter ensuite `AUTH_ENV_ENCRYPTION_KEY`, `AUTH_PASSWORD_ENCRYPTED`,
`AUTH_SECRET_KEY_ENCRYPTED`, `POSTGRES_PASSWORD` et
`POSTGRES_PASSWORD_ENCRYPTED` dans `docker/.env`. La sortie affiche aussi
`GENERATED_AUTH_PASSWORD`, qui est le mot de passe a saisir dans l'ecran
d'authentification. Docker PostgreSQL utilise `POSTGRES_PASSWORD` en clair au
demarrage de la base ; `POSTGRES_PASSWORD_ENCRYPTED` conserve la version
chiffree du meme secret.

La reponse contient `access_token`, `token_type` et `expires_in`. Tous les
appels aux routes protegees doivent ensuite envoyer :

```http
Authorization: Bearer <access_token>
```

### Inscription utilisateur

`POST /api/auth/register` cree un utilisateur avec un mot de passe stocke sous
forme d'empreinte non reversible et une adresse email non validee.
Cette route et la validation email sont publiques, car l'utilisateur n'a pas
encore de compte valide et ne peut pas encore posseder de token Bearer.

Exemple :

```json
{
  "email": "user@example.com",
  "password": "VeryStrongPassword123!"
}
```

Le backend genere un token de validation email, stocke uniquement son empreinte
SHA-256 en base, puis envoie un lien vers :

```http
GET /api/auth/verify-email?token=<token>
```

Variables utiles :

```bash
export BACKEND_PUBLIC_URL=https://api.example.com
export EMAIL_DELIVERY_MODE=smtp
export EMAIL_VERIFICATION_TOKEN_TTL_HOURS=24
export SMTP_FROM_EMAIL=noreply@example.com
export SMTP_HOST=smtp.example.com
export SMTP_PORT=587
export SMTP_USERNAME=...
export SMTP_PASSWORD=...
export SMTP_USE_TLS=true
```

En developpement, `EMAIL_DELIVERY_MODE=console` journalise l'email genere.

Tester l'envoi avec le conteneur backend deja demarre :

```bash
./test_email.sh --to destinataire@example.com
```

Pour tester la stack de production :

```bash
./test_email.sh -p --to destinataire@example.com
```

### Routes Disponibles

`GET /api/routes` retourne les routes backend et indique celles qui sont
publiques ou protegees par token Bearer.

Routes principales :

| Methode | Route | Role |
| --- | --- | --- |
| `GET` | `/collections/JeuxVideo/platforms` | Liste les plateformes ODS |
| `GET` | `/collections/JeuxVideo/home` | Retourne les statistiques d'accueil |
| `GET` | `/collections/JeuxVideo/search?platform=Switch&q=mario` | Liste ou filtre les jeux d'une plateforme |
| `GET` | `/collections/JeuxVideo/game-search?q=mario` | Recherche un jeu sur toutes les plateformes |
| `GET` | `/collections/JeuxVideo/column-values?platform=Switch` | Retourne les valeurs distinctes d'une plateforme |
| `GET` | `/collections/JeuxVideo/add-game-choices?platform=Switch` | Retourne les choix fusionnes et tries du formulaire |
| `GET` | `/collections/JeuxVideo/platform-image/Switch` | Retourne l'image embarquee de la plateforme |
| `POST` | `/collections/JeuxVideo/games` | Ajoute un jeu de collection |
| `PUT` | `/collections/JeuxVideo/games` | Modifie un jeu de collection |
| `DELETE` | `/collections/JeuxVideo/games` | Supprime un jeu de collection |
| `POST` | `/collections/JeuxVideo/wishlist/games` | Ajoute un jeu a la liste de souhaits |
| `PUT` | `/collections/JeuxVideo/wishlist/games` | Modifie un jeu de la liste de souhaits |
| `DELETE` | `/collections/JeuxVideo/wishlist/games` | Supprime un jeu de la liste de souhaits |
| `POST` | `/collections/JeuxVideo/cache/reset` | Vide le cache ODS |
| `GET` | `/collections/JeuxVideo/ods/download` | Telecharge le fichier ODS |

Toutes les routes du tableau exigent `Authorization: Bearer <access_token>`.
Les routes publiques sont `POST /auth/token`, `POST /api/auth/register`,
`GET /api/auth/verify-email` et `POST /api/auth/verify-email`. Les choix du
formulaire d'ajout sont fusionnes cote backend entre collection et liste de
souhaits, dedoublonnes en ignorant casse et espaces, nettoyes des valeurs
invalides comme `nan`, puis tries alphabetiquement.

Le formulaire `/add-game` reutilise la meme page pour ajouter vers la collection
ou vers la liste de souhaits. En mode liste de souhaits, le champ plateforme est
affiche sous le libelle `Plateforme`.

Avant chaque ecriture, une sauvegarde est creee dans le repertoire de backup
configure par `JEUXVIDEO_ODS_BACKUP_DIR` :

```text
collection.ods.backup-YYYYMMDDHHMMSSffffff
```

## Lancement Local

### Avec Docker Compose

Le projet peut tourner avec trois conteneurs :

- `backend` : API Flask exposee uniquement au reseau Docker interne
- `database` : PostgreSQL accessible uniquement par le backend via le reseau Docker interne `backend_data`
- `web` : Nginx qui sert le frontend React compile et proxifie `/api` et `/collections` vers le backend

Seul le fichier ODS defini par `JEUXVIDEO_ODS_FILE` est monte dans le conteneur backend, sans monter tout son dossier parent.
Les fichiers temporaires sont ecrits dans un `tmpfs` conteneur sur `/project/tmp`.
Les sauvegardes sont ecrites dans le repertoire monte `JEUXVIDEO_BACKUP_DIR`, disponible dans le conteneur sur `/project/backup`.
Les logs backend sont ecrits sur la sortie standard Docker et, si active,
dans le repertoire hote `BACKEND_LOG_HOST_DIR`, monte dans le conteneur sur
`/app/logs`. Le fichier actif tourne au changement de jour ou lorsque sa taille
depasse `BACKEND_LOG_FILE_MAX_BYTES`; `BACKEND_LOG_FILE_BACKUP_COUNT` limite le
nombre d'archives conservees.
PostgreSQL n'expose aucun port vers l'hote. Le backend recoit `DATABASE_URL` avec l'hote Docker interne `database`.
Au demarrage, le backend cree le schema PostgreSQL configure par `DB_SCHEMA_NAME`
s'il n'existe pas, applique les migrations Alembic, puis inscrit `APP_VERSION`
et la date de creation conservee dans `t_schema_version`.
Dans `docker/.env`, la valeur locale pointe vers `../collection.ods`.
Dans `docker/.env.example`, la valeur versionnable pointe vers `../collection-example.ods`.

Variables Docker principales :

| Variable | Role |
| --- | --- |
| `WEB_PORT` | Port HTTP expose par le conteneur web |
| `APP_HOME_TITLE` | Titre affiche dans l'interface |
| `JEUXVIDEO_ODS_FILE` | Fichier ODS monte dans le backend |
| `JEUXVIDEO_BACKUP_DIR` | Repertoire hote recevant les sauvegardes ODS |
| `BACKEND_LOG_LEVEL` | Niveau de log Python du backend |
| `BACKEND_LOG_FILE_ENABLED` | Active l'ecriture des logs backend sur disque |
| `BACKEND_LOG_HOST_DIR` | Repertoire hote recevant les logs backend |
| `BACKEND_LOG_FILE_NAME` | Nom du fichier de log actif dans le conteneur |
| `BACKEND_LOG_FILE_MAX_BYTES` | Taille maximale du fichier actif avant rotation |
| `BACKEND_LOG_FILE_BACKUP_COUNT` | Nombre maximal d'archives de logs conservees |
| `EMAIL_DELIVERY_MODE` | Mode email, `console` en local ou `smtp` en production |
| `SMTP_FROM_EMAIL` | Adresse expediteur des emails transactionnels |
| `SMTP_HOST` | Serveur SMTP du fournisseur transactionnel |
| `SMTP_PORT` | Port SMTP |
| `SMTP_USERNAME` | Identifiant SMTP du fournisseur transactionnel |
| `SMTP_PASSWORD` | Mot de passe ou cle SMTP du fournisseur transactionnel |
| `SMTP_USE_TLS` | Active STARTTLS pour l'envoi SMTP |
| `AUTH_USERNAME` | Identifiant autorise pour les actions protegees |
| `AUTH_ENV_ENCRYPTION_KEY` | Cle Fernet pour dechiffrer les secrets applicatifs |
| `AUTH_PASSWORD_ENCRYPTED` | Mot de passe applicatif chiffre |
| `AUTH_SECRET_KEY_ENCRYPTED` | Secret de signature des tokens chiffre |
| `AUTH_TOKEN_TTL_SECONDS` | Duree de validite des tokens Bearer |
| `APP_VERSION` | Version applicative inscrite dans `t_schema_version` |
| `DB_SCHEMA_NAME` | Schema PostgreSQL cree et migre au demarrage du backend |
| `POSTGRES_DB` | Nom de la base PostgreSQL |
| `POSTGRES_USER` | Utilisateur PostgreSQL |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL utilise par Docker |
| `POSTGRES_PASSWORD_ENCRYPTED` | Copie chiffree du mot de passe PostgreSQL |

Copier le fichier d'exemple d'environnement :

```bash
cp docker/.env.example docker/.env
```

Adapter ensuite `docker/.env` si besoin :

```bash
WEB_PORT=8080
JEUXVIDEO_ODS_FILE=../collection.ods
JEUXVIDEO_BACKUP_DIR=../backup
BACKEND_LOG_LEVEL=INFO
BACKEND_LOG_FILE_ENABLED=true
BACKEND_LOG_HOST_DIR=../logs
BACKEND_LOG_FILE_NAME=backend.log
BACKEND_LOG_FILE_MAX_BYTES=10485760
BACKEND_LOG_FILE_BACKUP_COUNT=30
EMAIL_DELIVERY_MODE=smtp
SMTP_FROM_EMAIL=noreply@cloud-collection-app.fr
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=remplacer-par-identifiant-smtp
SMTP_PASSWORD=remplacer-par-mot-de-passe-smtp
SMTP_USE_TLS=true
APP_VERSION=0.1
DB_SCHEMA_NAME=cloudcollectionapp
POSTGRES_DB=cloudcollectionapp
POSTGRES_USER=cloudcollectionapp
POSTGRES_PASSWORD=changer-ce-mot-de-passe
POSTGRES_PASSWORD_ENCRYPTED=fernet:generer-avec-scripts/generate_auth_env.py
```

Demarrer l'application :

```bash
cd docker
docker compose -f docker-compose.local.yml up --build
```

Ou depuis la racine :

```bash
./start.sh -d
```

L'application sera disponible sur :

```text
http://localhost:8080
```

Depuis un autre appareil du meme Wi-Fi, utiliser l'adresse IP locale du Mac :

```text
http://IP_DU_MAC:8080
```

Pour l'utiliser avec un nom local comme `cloud-collection-app.fr`, faire pointer ce nom vers l'IP locale du Mac dans le DNS local du reseau, puis acceder a :

```text
http://cloud-collection-app.fr:8080
```

Pour arreter :

```bash
cd docker
docker compose -f docker-compose.local.yml down
```

Ou depuis la racine :

```bash
./stop.sh -d
```

Pour supprimer aussi les donnees PostgreSQL de developpement, supprimer le
volume Docker `cloudcollectionapp_postgres_data`.

### Avec Docker Compose en production

La stack de production utilise un fichier Compose dedie avec Traefik et Let's Encrypt :

```bash
cd docker
docker compose -f docker-compose.online.yml up --build -d
```

Depuis la racine, le script de demarrage selectionne cette stack avec `-p` :

```bash
./start.sh -p
```

Les variables `DNS_NAME` et `LETSENCRYPT_EMAIL` doivent etre definies pour la stack online.
Pour arreter la stack de production :

```bash
./stop.sh -p
```

### Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
BACKEND_PORT=7777 python app.py
```

Le script `./test_backend.sh` utilise aussi Python 3.12 et recree automatiquement
`backend/.venv` si le virtualenv existant utilise une autre version.

Le backend tourne sur `http://localhost:7777`.

Le backend lance hors Docker doit recevoir `JEUXVIDEO_ODS_PATH` si le fichier
ODS n'est pas configure par ailleurs :

```bash
JEUXVIDEO_ODS_PATH=../collection-example.ods BACKEND_PORT=7777 python app.py
```

### Frontend

Dans un autre terminal :

```bash
cd frontend
npm install
BACKEND_PORT=7777 FRONTEND_PORT=7778 npm run dev
```

Le frontend tourne sur `http://localhost:7778`.

### Scripts Utilitaires

Depuis la racine :

```bash
./start.sh
./stop.sh
./start.sh -d
./stop.sh -d
```

Avec ports personnalises :

```bash
BACKEND_PORT=5000 FRONTEND_PORT=5173 ./start.sh
BACKEND_PORT=5000 FRONTEND_PORT=5173 ./stop.sh
```

## Build Frontend

```bash
cd frontend
npm run build
```

Le build de production est genere dans `frontend/dist/`.

## Tests

Lancer les tests backend depuis la racine :

```bash
./test_backend.sh
```

Le script verifie Python 3.12, cree ou recree `backend/.venv` si necessaire,
installe les dependances quand `requirements.txt` change, puis lance
`unittest`. Si `JEUXVIDEO_ODS_PATH` n'est pas deja defini, le script utilise la
fixture versionnee `collection-example.ods`.

Le frontend peut etre valide par :

```bash
cd frontend
npm run build
```

## CI Et Images Docker

Le projet contient un pipeline GitHub Actions dans :

```text
.github/workflows/ci.yml
.github/workflows/validate-pr.yml
```

Il execute les validations sur chaque `push` vers `main` et sur chaque tag Git,
avec detection des zones modifiees pour eviter les validations inutiles :

- les tests backend avec `./test_backend.sh` si `backend/`, `test_backend.sh`,
  `docker/backend.Dockerfile` ou `.github/workflows/ci.yml` change
- le build frontend avec `npm ci` puis `npm run build` si `frontend/`,
  `docker/frontend.Dockerfile` ou `.github/workflows/ci.yml` change
- le build et la publication des images Docker backend et frontend uniquement
  pour les tags `X.Y.Z`

Le workflow `validate-pr.yml` controle les pull requests : le titre doit suivre
le format Conventional Commits et la PR doit porter un label compatible avec les
release notes GitHub.

Sur un tag Git, les validations backend et frontend sont toujours executees
avant la publication Docker.

Les images sont publiees sur GitHub Container Registry :

```text
ghcr.io/sebastienbinda/cloudcollectionapp/backend:<version>
ghcr.io/sebastienbinda/cloudcollectionapp/backend:latest
ghcr.io/sebastienbinda/cloudcollectionapp/frontend:<version>
ghcr.io/sebastienbinda/cloudcollectionapp/frontend:latest
```

La version vient du tag Git qui declenche le workflow. Pour publier une version :

```bash
git tag 0.2.1
git push origin 0.2.1
```

Les images Docker ne sont pas publiees depuis les pushes de branche. Elles sont
publiees uniquement depuis un tag `X.Y.Z`, et ce tag devient la version des
images. Un tag ne respectant pas ce format echoue avant publication.

Le tag est aussi injecte au build Docker via `APP_VERSION`, ajoute aux images
comme label `org.opencontainers.image.version`, puis expose au frontend via
`VITE_APP_VERSION`. La version affichee dans l'interface vient donc de l'image
Docker publiee, pas d'une variable `APP_VERSION` dans `.env`.

Voir aussi `documentation/ci.md`.

## Notes De Maintenance

- Le fichier ODS reste la source de verite.
- PostgreSQL est present pour les futures fonctionnalites et n'est pas encore la source de verite de la collection.
- Les dossiers `node_modules/`, `dist/`, `.venv/` et les caches Python sont ignores par Git.
- L'ajout de jeu modifie le fichier ODS sur disque : verifier la sauvegarde si une modification doit etre annulee.
- Les sauvegardes ODS sont creees avant les ajouts, modifications et suppressions.
- Si la structure du fichier ODS change fortement, il faudra adapter les services `backend/services/ods/` et `GamesService`.

## Documentation Fonctionnelle

Les documents fonctionnels a maintenir sont dans `documentation/` :

- `documentation/authentication.md` : authentification, routes protegees et session frontend
- `documentation/register.md` : inscription utilisateur et validation email
- `documentation/site-plan.md` : redirection des pages sans session
- `documentation/about.md` : page About publique
- `documentation/menu.md` : menu principal
- `documentation/ci.md` : pipeline CI, version Docker et publication des images
