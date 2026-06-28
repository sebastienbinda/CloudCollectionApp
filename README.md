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

> [!IMPORTANT]
> Le code de cette application a ete genere avec l'aide de Codex et GPT-5.5.

CloudCollectionApp est une application web personnelle de gestion de collection
de jeux video. Elle permet d'importer une collection depuis un fichier ODS ou
CSV, de la consulter en ligne, de l'enrichir avec des informations privees et de
contribuer a un referentiel commun de plateformes, studios et jeux.

La version publique est disponible sur <https://www.cloud-collection.fr>.

## Fonctionnalites

- Import de collection utilisateur depuis LibreOffice Calc `.ods` ou CSV.
- Consultation de la collection personnelle avec statistiques, filtres, tris,
  details de jeux, prix, etats, regions, notes et descriptions privees.
- Liste de souhaits alimentee par les imports utilisateur, avec filtrage des
  jeux en cours d'achat.
- Bibliotheque commune de plateformes, studios et jeux, avec recherche et pages
  de detail.
- Proposition et moderation d'images de plateformes.
- Creation de compte, validation email, validation administrateur optionnelle et
  authentification par token Bearer.
- Partage temporaire de collection par lien, avec session `GUEST`, permissions
  par categorie et affichage optionnel des prix.
- Administration des utilisateurs, reset de la Bibliotheque globale et gestion
  des doublons signales.
- Backend Flask, frontend React/Vite, PostgreSQL, Docker Compose et publication
  d'images sur GitHub Container Registry.

## Documentation

Le README donne uniquement les commandes et concepts principaux. Les details
fonctionnels et techniques sont dans `documentation/` :

- [documentation/backend-api.md](documentation/backend-api.md) : routes et
  contrats API.
- [documentation/backend-arch.md](documentation/backend-arch.md) : architecture
  backend Flask.
- [documentation/frontend-arch.md](documentation/frontend-arch.md) : architecture
  frontend React/Vite.
- [documentation/database.md](documentation/database.md) : schema PostgreSQL,
  migrations et persistance production.
- [documentation/authentication.md](documentation/authentication.md) :
  authentification, profils et sessions.
- [documentation/register.md](documentation/register.md) : inscription et
  validation email.
- [documentation/share.md](documentation/share.md) : partage temporaire de
  collection.
- [documentation/collection.md](documentation/collection.md) : consultation de la
  collection utilisateur.
- [documentation/import.md](documentation/import.md) : workflow d'import ODS/CSV.
- [documentation/import-mapping.md](documentation/import-mapping.md) : regles de
  conversion des valeurs importees.
- [documentation/reader.md](documentation/reader.md) : lecteurs de fichiers de
  collection.
- [documentation/bibliotheque.md](documentation/bibliotheque.md) : Bibliotheque
  commune, images et administration.
- [documentation/users.md](documentation/users.md) : administration utilisateur.
- [documentation/site-plan.md](documentation/site-plan.md),
  [documentation/menu.md](documentation/menu.md) et
  [documentation/about.md](documentation/about.md) : navigation, menu et page
  publique About.
- [documentation/ci.md](documentation/ci.md) : CI, images Docker et archive de
  deploiement.

## Structure

- `backend/` : API Flask, services metier, repositories, migrations et tests.
- `frontend/` : application React/Vite.
- `docker/` : fichiers utiles a la generation des images et au developpement
  Docker local.
- `runtime/` : fichiers necessaires au deploiement production.
- `scripts/` : scripts de test, generation et livraison.
- `.github/workflows/` : pipeline CI.

## Deploiement Local

### Docker Compose

Depuis la racine du projet :

```bash
cp runtime/.env.local.example runtime/.env
./runtime/start.sh -d
```

Services locaux :

- application : `http://localhost:8080`
- Mailpit : `http://localhost:8025`
- PostgreSQL : `localhost:5432`

Arret :

```bash
./runtime/stop.sh -d
```

Le mode local utilise `docker/docker-compose.local.yml` et construit les images
depuis le code source. Les variables locales se configurent dans `runtime/.env`.

### Backend Seul

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
BACKEND_PORT=7777 python app.py
```

Backend : `http://localhost:7777`

### Frontend Seul

```bash
cd frontend
npm install
BACKEND_PORT=7777 FRONTEND_PORT=7778 npm run dev
```

Frontend : `http://localhost:7778`

## Tests Et Build

Backend :

```bash
./scripts/test_backend.sh
```

Frontend :

```bash
cd frontend
npm test
npm run build
```

Images Docker locales :

```bash
docker compose -f docker/docker-compose.local.yml build backend
docker compose -f docker/docker-compose.local.yml build web
```

## Deploiement Production

La production utilise les images publiees dans GitHub Container Registry et une
archive de deploiement minimale `cloud-application-deploy.zip`. Cette archive est
generee par la CI sur les tags de release `X.Y.Z` et contient uniquement :

- `runtime/start.sh`
- `runtime/stop.sh`
- `runtime/secure.sh`
- `runtime/prepare_directories.sh`
- `runtime/docker-compose.online.yml`
- `runtime/.env.production.example`

Images publiees :

```text
ghcr.io/sebastienbinda/cloudcollectionapp/backend:<version>
ghcr.io/sebastienbinda/cloudcollectionapp/frontend:<version>
ghcr.io/sebastienbinda/cloudcollectionapp/age-secrets:latest
```

### 1. Telecharger Et Extraire L'Archive

Depuis la page de pipeline GitHub Actions ou GitLab CI du tag de release,
telecharger l'artefact `cloud-application-deploy.zip`, puis l'extraire sur le
serveur :

```bash
unzip cloud-application-deploy.zip
cd cloud-application-deploy
cp runtime/.env.production.example runtime/.env
```

Configurer ensuite `runtime/.env`, notamment :

- `APP_VERSION` avec le tag applicatif a deployer.
- `RUNTIME_UID` et `RUNTIME_GID` avec l'identite Unix non-root utilisee par les
  conteneurs applicatifs `backend` et `web`.
- `DNS_NAME`, `BACKEND_PUBLIC_URL`, `FRONTEND_PUBLIC_URL`.
- `APPLICATION_WORKDIR` avec le repertoire parent commun des donnees de travail
  de l'application.
- `USERS_WORKSPACE`, `BACKEND_IMG_HOST_DIR`, `BACKEND_LOG_HOST_DIR`,
  `POSTGRES_DATA_HOST_DIR` et `TRAEFIK_LETSENCRYPT_HOST_DIR` si les sous-dossiers
  par defaut de `APPLICATION_WORKDIR` ne conviennent pas.
- les variables SMTP non secretes.
- `AGE_SECRETS_ARCHIVE_FILE` et `AGE_SECRETS_IDENTITY_FILE` si les chemins par
  defaut ne conviennent pas.

Le demarrage cree et valide automatiquement l'arborescence hote via
`runtime/prepare_directories.sh`. Avec les valeurs par defaut, tous les
repertoires persistants sont sous `/var/lib/cloudcollectionapp` :

```text
/var/lib/cloudcollectionapp/users-workspace
/var/lib/cloudcollectionapp/images
/var/lib/cloudcollectionapp/logs
/var/lib/cloudcollectionapp/postgres-data
/var/lib/cloudcollectionapp/letsencrypt
```

Les repertoires ecrits par `backend` sont verifies avec le proprietaire
`RUNTIME_UID:RUNTIME_GID`. Si le script ne peut pas creer ou corriger les
proprietaires, relancer le demarrage avec des droits suffisants ou preparer les
droits manuellement.

`backend` et `web` sont lances avec `user: RUNTIME_UID:RUNTIME_GID`. `web`
ecoute donc sur le port interne non privilegie `8080`, relaye par Traefik.
PostgreSQL et Traefik gardent le comportement non-root/root controle par leurs
images officielles, car forcer ces services au meme UID runtime peut casser
l'initialisation de la base, les certificats ou l'ecoute des ports 80/443.

### 2. Creer Ou Reutiliser Les Secrets Age

En production, les secrets ne doivent pas etre stockes en clair dans
`runtime/.env` ni durablement sur disque. `./runtime/start.sh -p` decrypte
l'archive age dans un repertoire temporaire en memoire sous `/dev/shm`, prepare
les fichiers Docker secrets, genere `DATABASE_URL`, lance Docker Compose, puis
supprime les fichiers dechiffres. Si `/dev/shm` n'existe pas sur le serveur,
configurer `PRODUCTION_SECRETS_TMP_PARENT` vers un autre tmpfs prive.

Par defaut, l'archive attendue est :

```text
runtime/secrets.tar.gz.age
```

Elle doit contenir ces fichiers a sa racine :

```text
AUTH_ENV_ENCRYPTION_KEY
AUTH_PASSWORD_ENCRYPTED
AUTH_SECRET_KEY_ENCRYPTED
POSTGRES_PASSWORD
SMTP_PASSWORD
```

Si une archive existe deja, copier `secrets.tar.gz.age` sur le serveur et
renseigner l'identite age privee via `AGE_SECRETS_IDENTITY_FILE` ou avec la
configuration age de l'utilisateur systeme.

Pour creer une nouvelle archive, preparer un dossier local avec les cinq fichiers
ci-dessus, puis chiffrer :

```bash
./runtime/secure.sh encrypt \
  --source-dir runtime/secrets-src \
  --archive runtime/secrets.tar.gz.age \
  --recipient age1...
```

Pour lire ou mettre a jour un secret existant :

```bash
./runtime/secure.sh read \
  --archive runtime/secrets.tar.gz.age \
  --name POSTGRES_PASSWORD \
  --identity age-identity.txt

./runtime/secure.sh set \
  --archive runtime/secrets.tar.gz.age \
  --name SMTP_PASSWORD \
  --value "nouveau-secret" \
  --identity age-identity.txt \
  --recipient age1...
```

### 3. Demarrer La Production

Depuis le repertoire extrait :

```bash
./runtime/start.sh -p
```

Le script :

- aligne `runtime/.env` sur le modele `runtime/.env.production.example` ;
- verifie que `RUNTIME_UID` et `RUNTIME_GID` sont numeriques ;
- refuse de continuer si des variables obligatoires viennent d'etre ajoutees ;
- cree et valide l'arborescence configuree sous `APPLICATION_WORKDIR` ;
- decrypte les secrets age dans un repertoire temporaire en memoire ;
- prepare les fichiers Docker secrets et supprime les fichiers dechiffres apres
  le lancement ;
- lance `runtime/docker-compose.online.yml`.

Toute mise a jour ou recreation des conteneurs doit repasser par
`./runtime/start.sh -p`, afin que les secrets soient redéchiffrés temporairement
le temps du lancement Compose.

Arret :

```bash
./runtime/stop.sh -p
```

Les details de CI, d'images, d'archive et de compose production sont dans
[documentation/ci.md](documentation/ci.md). Les regles de persistance PostgreSQL
et migrations sont dans [documentation/database.md](documentation/database.md).
