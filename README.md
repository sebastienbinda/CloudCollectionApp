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
- Ecran de statistiques detaillees par plateforme, annees de sortie, annees
  d'achat et meilleurs jeux notes.
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
- Backend Flask, frontend React/Vite avec Chart.js pour les graphiques,
  PostgreSQL, Docker Compose et publication d'images sur GitHub Container
  Registry.

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
- [documentation/deploy.md](documentation/deploy.md) : deploiement, archive de
  livraison, Docker Compose runtime et secrets production.
- [documentation/authentication.md](documentation/authentication.md) :
  authentification, profils et sessions.
- [documentation/register.md](documentation/register.md) : inscription et
  validation email.
- [documentation/share.md](documentation/share.md) : partage temporaire de
  collection.
- [documentation/collection.md](documentation/collection.md) : consultation de la
  collection utilisateur.
- [documentation/statistics.md](documentation/statistics.md) : ecran et API de
  statistiques detaillees de collection.
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
./runtime/deploy.sh -d
```

Services locaux :

- application : `http://localhost:8080`
- Mailpit : `http://localhost:8025`
- PostgreSQL : `localhost:5432`

Arret :

```bash
./runtime/deploy.sh -d -s
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
archive de deploiement minimale `cloud-application-deploy-<version>.zip`. Cette
archive est generee par la CI sur les tags de release `X.Y.Z`, publiee comme
asset de release GitHub, et contient uniquement :

- `deploy.sh`
- `secure.sh`
- `age_identity_cleanup.sh`
- `prepare_directories.sh`
- `userns_remap_detection.sh`
- `docker-compose.online.yml`
- `.env.production.example`

Images publiees :

```text
ghcr.io/sebastienbinda/cloudcollectionapp/backend:<version>
ghcr.io/sebastienbinda/cloudcollectionapp/frontend:<version>
ghcr.io/sebastienbinda/cloudcollectionapp/age-secrets:latest
```

### 1. Telecharger Et Extraire L'Archive

Depuis le serveur de production, telecharger la derniere archive de deploiement
publiee en release GitHub, puis l'extraire :

```bash
REPOSITORY="sebastienbinda/cloudcollectionapp"
LATEST_RELEASE_URL="$(curl -fsSLI -o /dev/null -w '%{url_effective}' "https://github.com/${REPOSITORY}/releases/latest")"
APP_VERSION="${LATEST_RELEASE_URL##*/}"

curl -fL \
  -o "cloud-application-deploy-${APP_VERSION}.zip" \
  "https://github.com/${REPOSITORY}/releases/download/${APP_VERSION}/cloud-application-deploy-${APP_VERSION}.zip"

mkdir -p cloud-application-deploy
unzip -o "cloud-application-deploy-${APP_VERSION}.zip" -d cloud-application-deploy
cd cloud-application-deploy
mkdir -p /etc/cloudcollectionapp/deploy-env
cp .env.production.example /etc/cloudcollectionapp/deploy-env/.env
```

Configurer ensuite `/etc/cloudcollectionapp/deploy-env/.env`, notamment :

- `APP_VERSION` avec le tag applicatif a deployer.
- `RUNTIME_UID` et `RUNTIME_GID` avec l'identite Unix non-root utilisee par les
  conteneurs applicatifs `backend` et `web`.
- `RUNTIME_HOST_UID` et `RUNTIME_HOST_GID` avec l'identite Unix vue par l'hote
  pour les repertoires bind mountes. Sans Docker `userns-remap`, garder les
  memes valeurs que `RUNTIME_UID` et `RUNTIME_GID`. Avec Docker `userns-remap`,
  renseigner les UID/GID remappes de l'hote: debut de plage `/etc/subuid` ou
  `/etc/subgid` plus `RUNTIME_UID` ou `RUNTIME_GID`. Par exemple, avec une plage
  `dockremap:100000:65536` et `RUNTIME_UID=10001`, `RUNTIME_HOST_UID=110001`.
- `POSTGRES_HOST_ROOT_UID` et `POSTGRES_HOST_ROOT_GID`. Sans Docker
  `userns-remap`, conserver `0:0`. Avec Docker `userns-remap`, renseigner les
  UID/GID hotes correspondant au root du conteneur PostgreSQL, souvent le debut
  des plages `dockremap` dans `/etc/subuid` et `/etc/subgid`.
- `DNS_NAME`, `BACKEND_PUBLIC_URL`, `FRONTEND_PUBLIC_URL`.
- `APPLICATION_WORKDIR` avec le repertoire parent commun des donnees de travail
  de l'application.
- `USERS_WORKSPACE`, `BACKEND_IMG_HOST_DIR`, `BACKEND_LOG_HOST_DIR`,
  `POSTGRES_DATA_HOST_DIR` et `TRAEFIK_LETSENCRYPT_HOST_DIR` si les sous-dossiers
  par defaut de `APPLICATION_WORKDIR` ne conviennent pas.
- les variables SMTP non secretes.

Le demarrage cree et valide automatiquement l'arborescence hote via
`prepare_directories.sh`. Avec les valeurs par defaut, tous les
repertoires persistants sont sous `/var/lib/cloudcollectionapp` :

```text
/var/lib/cloudcollectionapp/users-workspace
/var/lib/cloudcollectionapp/images
/var/lib/cloudcollectionapp/logs
/var/lib/cloudcollectionapp/postgres-data
/var/lib/cloudcollectionapp/letsencrypt
```

Les repertoires ecrits par `backend` sont verifies avec le proprietaire hote
`RUNTIME_HOST_UID:RUNTIME_HOST_GID`. Le repertoire PostgreSQL
`POSTGRES_DATA_HOST_DIR` est prepare avec
`POSTGRES_HOST_ROOT_UID:POSTGRES_HOST_ROOT_GID`, afin que le root remappe du
conteneur PostgreSQL puisse initialiser puis corriger les droits internes de la
base. Quand Docker `userns-remap` est actif et que les plages de remap sont
lisibles, le script verifie que ces identifiants correspondent au remap Docker
avant de preparer les repertoires. Si le script ne peut pas creer ou corriger
les proprietaires, relancer le demarrage avec des droits suffisants ou preparer
les droits manuellement. Avec le chemin par defaut
`/var/lib/cloudcollectionapp`, `./deploy.sh -p -e <repertoire-env>` peut demander le mot de
passe `sudo` uniquement pour creer l'arborescence hote et appliquer les
proprietaires attendus.

`backend` et `web` sont lances avec `user: RUNTIME_UID:RUNTIME_GID`. `web`
ecoute donc sur le port interne non privilegie `8080`, relaye par Traefik.
PostgreSQL garde le comportement non-root/root controle par son image
officielle, car forcer ce service au meme UID runtime peut casser
l'initialisation de la base. Traefik garde aussi son comportement officiel et
utilise `userns_mode: host` en production, car le provider Docker doit lire
`/var/run/docker.sock`; ce socket donne deja des privileges eleves sur le daemon
Docker et ne peut pas etre lu par un root remappe.

### 2. Preparer Les Secrets Age

En production, les secrets ne doivent pas etre stockes en clair dans
le fichier `.env` ni durablement sur disque. `./deploy.sh -p -e <repertoire-env>` decrypte
l'archive age dans un repertoire temporaire compatible avec les bind mounts
Docker, prepare les fichiers Docker secrets, genere `DATABASE_URL`, lance
Docker Compose, puis supprime les fichiers dechiffres. Par defaut, le script
utilise `/tmp` si le daemon Docker peut y monter un fichier secret. Pour forcer
un autre emplacement, definir `PRODUCTION_SECRETS_TMP_PARENT`, par exemple
`PRODUCTION_SECRETS_TMP_PARENT=/dev/shm` si ce chemin est visible par Docker
Compose sur l'hote. Le dechiffrement utilise l'image Docker
`ghcr.io/sebastienbinda/cloudcollectionapp/age-secrets:latest`; la commande
`age` n'a pas besoin d'etre installee sur l'hote.

Deux cas sont possibles.

#### Cas 1 : premiere installation, creer l'archive

Generer la cle age et l'archive des secrets :

```bash
./secure.sh bootstrap
```

La commande demande les valeurs des secrets, cree l'archive chiffree et supprime
les fichiers temporaires en clair. Elle produit :

```text
.age/identity.txt          # cle privee age a conserver dans un lieu protege
env/secrets.tar.gz.age     # archive chiffree utilisee au demarrage
```

`identity.txt` est indispensable pour modifier ou regenerer l'archive.
Conserver une copie de cette cle hors depot et hors serveur avant toute
suppression. Pour utiliser le repertoire d'environnement externe, copier ensuite
`.age/identity.txt` vers `deploy-env/identity.txt` et
`env/secrets.tar.gz.age` vers `deploy-env/secrets.tar.gz.age`.

#### Cas 2 : archive deja generee

Deposer l'archive age et la cle privee age dans le repertoire d'environnement :

```bash
cp /chemin/securise/identity.txt /etc/cloudcollectionapp/deploy-env/identity.txt
cp /chemin/securise/secrets.tar.gz.age /etc/cloudcollectionapp/deploy-env/secrets.tar.gz.age
chmod 600 /etc/cloudcollectionapp/deploy-env/identity.txt /etc/cloudcollectionapp/deploy-env/secrets.tar.gz.age
```

Pour regrouper la configuration de deploiement dans un repertoire externe, ce
repertoire peut contenir directement les trois fichiers attendus par
`./deploy.sh -p -e <repertoire-env>` :

```text
deploy-env/.env
deploy-env/identity.txt
deploy-env/secrets.tar.gz.age
```

Apres un demarrage production reussi, `deploy.sh` propose de supprimer
la cle `identity.txt` utilisee depuis son emplacement par defaut ou depuis le
repertoire `-e`. Ne confirmer la suppression que si une copie de la cle est
conservee ailleurs.

Pour lire ou mettre a jour un secret existant :

```bash
./secure.sh read --name POSTGRES_PASSWORD
./secure.sh set \
  --name SMTP_PASSWORD \
  --value "nouveau-secret"
```

### 3. Demarrer La Production

Depuis le repertoire extrait :

```bash
./deploy.sh -p -e /etc/cloudcollectionapp/deploy-env
```

Si les fichiers d'environnement et de secrets sont regroupes dans un autre
repertoire, remplacer `/etc/cloudcollectionapp/deploy-env` par ce chemin.

Le script :

- aligne le fichier `.env` selectionne sur le modele
  `.env.production.example` en conservant les valeurs deja configurees ;
- verifie que `RUNTIME_UID`, `RUNTIME_GID`, `RUNTIME_HOST_UID` et
  `RUNTIME_HOST_GID` sont numeriques ;
- refuse de continuer si des variables obligatoires viennent d'etre ajoutees ;
- cree et valide l'arborescence configuree sous `APPLICATION_WORKDIR`, avec
  `sudo` si le chemin de production le necessite ;
- decrypte l'archive `secrets.tar.gz.age` avec `identity.txt` depuis les chemins
  par defaut ou depuis le repertoire `-e` ;
- prepare les fichiers Docker secrets et supprime les fichiers dechiffres apres
  le lancement ;
- lance `docker-compose.online.yml`.

Avec `-p -r`, le script telecharge les images publiees `backend` et `web`
referencees par `APP_VERSION`, puis force la recreation des conteneurs. Il ne
construit pas les images localement en production.

Toute mise a jour ou recreation des conteneurs doit repasser par
`./deploy.sh -p -e <repertoire-env>`, afin que les secrets soient redéchiffrés
temporairement le temps du lancement Compose.

Arret :

```bash
./deploy.sh -p -s -e /etc/cloudcollectionapp/deploy-env
```

Les details complets de deploiement sont dans
[documentation/deploy.md](documentation/deploy.md). Les details de CI et
d'images publiees sont dans [documentation/ci.md](documentation/ci.md). Les
regles de persistance PostgreSQL et migrations sont dans
[documentation/database.md](documentation/database.md).
