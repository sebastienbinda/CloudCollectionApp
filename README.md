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

Le code de cette application a ete realise a l'aide de Codex et de l'API GPT 5.5.

Application web personnelle qui transforme un fichier de collection LibreOffice
Calc `.ods` en site en ligne accessible a tout moment. Chaque utilisateur garde
sa collection privee rattachee a son compte, tout en contribuant a enrichir une
base commune de jeux, plateformes et studios.

Le premier fichier ODS importe initialise la collection personnelle, et les
imports suivants peuvent ajouter des jeux sans reinitialiser la collection. La
consultation de collection s'appuie ensuite sur PostgreSQL, tandis que le
dernier fichier ODS utilisateur reste telechargeable en brut. Le backend expose
une API securisee pour proteger les donnees utilisateur et alimenter le
referentiel commun, tandis que le frontend fournit une interface web de
consultation, recherche et import.

## Version Deployee

La derniere version release de l'application est deployee en ligne. Vous pouvez
voir le resultat a cette adresse : https://www.cloud-collection.fr

## Fonctionnalites

- Tableau de bord de collection avec somme et moyenne des prix, globalement et par plateforme.
- Bibliotheque publique des plateformes, studios et jeux du referentiel commun.
- Images publiques acceptees sur les fiches plateformes de la Bibliotheque,
  avec proposition d'image par utilisateur connecte.
- Referentiel de plateformes et alias fourni par defaut depuis les CSV backend.
- Navigation par plateforme, detail de jeu, detail de plateforme et consultation de la collection personnelle.
- Page Liste de souhaits pour consulter les jeux importes avec
  `wishlist=true`.
- Recherche globale par nom de jeu.
- Filtres et tris de collection apres authentification.
- Import de collection ODS personnelle et ajout par nouvel import pour les utilisateurs inscrits.
- Page About publique, authentification Bearer et creation de compte avec
  pseudonyme unique, validation email puis validation administrateur optionnelle.
- Activation des liens `/collection/share/<token>` en session GUEST revocable,
  avec retrait immediat du token de l'URL et redirection selon les permissions.
- Administration utilisateur et telechargement brut du fichier ODS utilisateur.
- Reset administrateur de la Bibliotheque globale depuis les imports utilisateur stockes.
- Moderation administrateur des images de plateformes proposees.
- Initialisation PostgreSQL par Alembic pour les fonctionnalites utilisateur.

## Architecture Globale

Le projet est separe en deux applications :

- `backend/` : API Python Flask.
- `frontend/` : application React construite avec Vite.

En developpement, Vite proxifie les routes `/api` et `/collections` vers Flask.
En Docker, le service `web` sert le frontend compile avec Nginx et proxifie vers
le service `backend`.

## Backend

Technologies principales :

- Python 3.12
- Flask
- SQLAlchemy et Alembic
- PostgreSQL
- pandas, odfpy et XML/ZIP standard library pour l'import ODS utilisateur

Organisation :

- `backend/app.py` : composition Flask, initialisation runtime, enregistrement des controllers et protection globale.
- `backend/controllers/` : endpoints HTTP et mapping des reponses.
- `backend/services/` : services metier et infrastructure organises par domaine.
- `backend/services/ods/` : lecture d'import ODS utilisateur, archive, cache et secours XML.
- `backend/services/collection/imports/` : contrats et mapping de valeurs reutilisables par tous les formats d'import.
- `backend/services/database/` : configuration SQLAlchemy, ORM, repositories et schema.
- `backend/tests/` : tests backend par couche.

Regles detaillees :

- Architecture backend : `documentation/backend-arch.md`
- API backend : `documentation/backend-api.md`
- Authentification : `documentation/authentication.md`
- Base de donnees : `documentation/database.md`

## Frontend

Technologies principales :

- React
- Vite
- CSS classique

Organisation :

- `frontend/src/App.jsx` : point d'entree React et composition du cadre applicatif.
- `frontend/src/components/` : pages, vues, dialogues et composants reutilisables.
- `frontend/src/services/` : clients API et services frontend.
- `frontend/src/hooks/` : hooks React organises par domaine.
- `frontend/src/styles.css` et `frontend/src/styles/` : styles de l'interface.

Domaines de hooks :

- `hooks/app/` : session, droits backend et view-model principal.
- `hooks/navigation/` : vue courante, plateforme selectionnee et URL.
- `hooks/collection/` : rechargement transversal et onboarding d'import.
- `hooks/home/` : statistiques Ma collection et recherche globale.
- `hooks/library/` : Bibliotheque publique, recherche, tri et pagination serveur.
- `hooks/platforms/` : plateformes de la collection utilisateur lues depuis SQL.
- `hooks/games/` : jeux de la collection utilisateur, detail de jeu, tri, filtres et actions futures.

Regles detaillees :

- Architecture frontend : `documentation/frontend-arch.md`
- Plan de navigation : `documentation/site-plan.md`
- Menu : `documentation/menu.md`
- Page About : `documentation/about.md`

## Import ODS Utilisateur

Le backend ne consulte plus de collection globale depuis un fichier ODS. Les
vues Ma collection et Liste de souhaits lisent PostgreSQL via les endpoints
`/collections/videogames/**`.

Variables principales :

- `USERS_WORKSPACE` : repertoire hote monte par Docker Compose dans `/users/workspace`.
- `USER_COLLECTION_MAX_UPLOAD_BYTES` : taille maximale d'upload d'une collection
  utilisateur, appliquee a Flask et au proxy Nginx du service `web`.
- `BACKEND_IMG_DIR` : repertoire conteneur utilise par le backend pour stocker
  les images de plateformes. Valeur par defaut : `/images`.
- `PLATFORM_IMAGE_MAX_UPLOAD_BYTES` : taille maximale d'upload d'une image de
  plateforme. Valeur par defaut : `10485760`.
- `PLATFORM_IMAGE_MAX_PENDING_IMAGES_PER_USER` : nombre maximal d'images de
  plateformes en attente par utilisateur. Valeur par defaut : `20`.
- `PLATFORM_IMAGE_MAX_PENDING_BYTES_PER_USER` : taille maximale cumulee des
  images de plateformes en attente par utilisateur. Valeur par defaut :
  `52428800`.
- `PLATFORM_IMAGE_MAX_TOTAL_BYTES` : taille maximale totale des images de
  plateformes stockees sur disque. Valeur par defaut : `1073741824`.
  Les quotas utilisent la colonne `t_platform_image.file_size_bytes`, renseignee
  lors de l'ajout d'une image, afin d'eviter un recalcul disque a chaque upload.
- `BACKEND_IMG_HOST_DIR` : repertoire hote monte par Docker Compose dans
  `BACKEND_IMG_DIR` pour persister les images de plateformes. En production, le
  chemin doit etre absolu, exister et etre sauvegardable.
- `MATCHING_LOW_LVL_RATING` : score minimal de matching plateforme pour importer
  avec verification administrateur. Valeur par defaut : `25`.
- `MATCHING_HIGH_LEVEL_RATING` : score de matching plateforme a partir duquel
  l'import est accepte sans warning de verification. Valeur par defaut : `75`.
- `REGION_MATCH_LIMIT` : score minimal de similarite pour rattacher une region
  importee a un code autorise. Valeur par defaut : `60`.
- `ETAT_MATCH_LIMIT` : score minimal de similarite pour rattacher un etat
  importe a un libelle francais ou anglais. Valeur par defaut : `60`.
- `ADMIN_NOTIFICATION_EMAIL` : destinataire des notifications d'inscription en
  attente de validation administrateur, des rapports de fin d'import utilisateur
  des rapports de reset Bibliotheque et des propositions d'images de
  plateformes.
- `ADMIN_ACCOUNT_VALIDATION_ENABLED` : active la validation administrateur apres
  validation email utilisateur. Valeur par defaut : `true`.
- `POSTGRES_DATA_HOST_DIR` : chemin absolu du repertoire hote utilise en
  production pour persister les donnees PostgreSQL du conteneur `database`.
- `TRAEFIK_LETSENCRYPT_HOST_DIR` : chemin absolu du repertoire hote monte dans
  `/letsencrypt` pour persister le compte ACME, les certificats TLS et leurs cles
  entre les recreations du conteneur Traefik. Ce repertoire doit etre prive,
  sauvegarde et ne doit jamais etre publie dans le depot.

Le backend journalise chaque appel REST avec la methode, le chemin, l'endpoint,
le statut HTTP, la duree et l'adresse cliente. Les reponses HTTP en erreur
(`4xx` et `5xx`) sont emises au niveau `ERROR`; lorsqu'une reponse JSON contient
un champ `error`, son message borne est inclus sans journaliser le corps de la
requete ni ses parametres.

Un fichier exemple versionnable est fourni :

```text
collection-example.ods
```

Structure fonctionnelle attendue pour l'import :

- le fichier est d'abord depose dans le workspace utilisateur, puis analyse
  pour proposer les onglets disponibles ;
- apres analyse, l'application peut proposer de reutiliser la derniere
  configuration d'import sauvegardee ;
- un onglet par plateforme ou une configuration explicite des onglets ;
- en mode multi-onglets avec layout partage, l'utilisateur peut lister les
  onglets a importer ou les onglets a exclure ;
- l'import peut lire une wishlist depuis aucun emplacement, un onglet dedie ou
  une colonne dediee ;
- apres succes, l'interface affiche un resume d'import et propose d'ouvrir Ma
  collection.
- l'import peut associer des informations privees optionnelles a chaque jeu
  (prix positif ou nul tronque a deux decimales et unite ISO, achat, note, etat,
  contenu, region et description),
  visibles uniquement dans le detail de la collection connectee ;
- les listes collection et wishlist affichent le drapeau de region sur desktop
  et mobile lorsqu'une region est renseignee ;
- si `ADMIN_NOTIFICATION_EMAIL` est configure, le backend notifie
  l'administrateur apres chaque validation email utilisateur et envoie un seul
  rapport administrateur en fin d'import avec le contexte, les compteurs, la
  configuration validee, la duree et les warnings eventuels ;
- depuis Configuration, un utilisateur non `ADMIN` avec collection peut ouvrir
  le parcours `/collection/import` pour ajouter les jeux d'un nouveau fichier
  sans supprimer sa collection actuelle ;
- depuis Configuration, un utilisateur non `ADMIN` peut reinitialiser sa
  collection pour supprimer les associations importees, effacer le fichier
  serveur et revenir au parcours `/collection/import`.
- depuis Configuration, un utilisateur `ADMIN` peut lancer un reset asynchrone
  de la Bibliotheque globale. Le reset reconstruit le referentiel depuis les
  fichiers utilisateurs stockes, refuse temporairement les imports utilisateur,
  puis envoie le rapport final a `ADMIN_NOTIFICATION_EMAIL`.
- depuis Configuration, un utilisateur `ADMIN` peut mettre a jour le catalogue
  plateformes et alias en ajoutant en base les entrees absentes des CSV backend.
- depuis Configuration, un utilisateur `ADMIN` peut ouvrir la page dediee
  `/configuration/images-plateformes` pour moderer les images de plateformes
  proposees, les accepter, les refuser ou definir l'image principale.

## Lancement Local

### Docker Compose

Copier puis adapter l'environnement :

```bash
cp docker/.env.example docker/.env
```

Demarrer depuis la racine :

```bash
./start.sh -d
```

Ou depuis `docker/` :

```bash
docker compose -f docker-compose.local.yml up --build
```

En production, `docker/docker-compose.online.yml` exige
`POSTGRES_DATA_HOST_DIR` avec un chemin absolu existant et sauvegardable pour
monter les donnees PostgreSQL dans `/var/lib/postgresql/data`.
Il exige egalement `TRAEFIK_LETSENCRYPT_HOST_DIR` avec un chemin absolu prive et
sauvegardable pour monter les donnees ACME dans `/letsencrypt`. Le fichier
`acme.json` contient des cles privees et ne doit jamais etre affiche, partage ou
versionne.
Il exige aussi `BACKEND_IMG_HOST_DIR` avec un chemin absolu existant et
sauvegardable pour persister les images de plateformes.

Services locaux :

- application : `http://localhost:8080`
- Mailpit : `http://localhost:8025`
- PostgreSQL : `localhost:5432`

Arreter :

```bash
./stop.sh -d
```

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

## Validation

Backend :

```bash
./test_backend.sh
```

Frontend :

```bash
cd frontend
node --test tests/collectionShareSession.test.js
npm run build
```

Images Docker locales :

```bash
docker compose -f docker/docker-compose.local.yml build backend
docker compose -f docker/docker-compose.local.yml build web
```

## CI Et Livraison

Les workflows GitHub Actions sont dans :

```text
.github/workflows/ci.yml
.github/workflows/validate-pr.yml
```

La CI valide les pull requests, les branches et les tags selon les zones
modifiees. Le job Docker publie les images uniquement sur tag `X.Y.Z`.

Images publiees :

```text
ghcr.io/sebastienbinda/cloudcollectionapp/backend:<version>
ghcr.io/sebastienbinda/cloudcollectionapp/frontend:<version>
```

Déploiement production :

```bash
docker compose --env-file docker/.env -f docker/docker-compose.online.yml pull
docker compose --env-file docker/.env -f docker/docker-compose.online.yml up -d
```

Le compose de production utilise les images GitHub Container Registry sans les
builder localement. La variable `APP_VERSION` du fichier `.env` choisit le tag
des images `backend` et `frontend`; si elle est absente, le tag `latest` est
utilisé. Le stack de production démarre aussi PostgreSQL et construit
`DATABASE_URL` depuis `POSTGRES_DB`, `POSTGRES_USER` et `POSTGRES_PASSWORD`.

Documentation CI : `documentation/ci.md`.

## Documentation

Documents fonctionnels et techniques principaux :

- `documentation/backend-api.md` : routes et contrats API backend.
- `documentation/backend-arch.md` : architecture Flask/backend.
- `documentation/frontend-arch.md` : architecture React/Vite.
- `documentation/authentication.md` : authentification, routes protegees et session frontend.
- `documentation/bibliotheque.md` : consultation publique du referentiel commun et reset administrateur.
- `documentation/collection.md` : consultation SQL de la collection utilisateur.
- `documentation/import.md` : regles fonctionnelles d'import de collection utilisateur.
- `documentation/import-mapping.md` : mapping synthetique des valeurs importees vers les valeurs persistees.
- `documentation/register.md` : inscription utilisateur et validation email.
- `documentation/users.md` : administration des utilisateurs.
- `documentation/site-plan.md` : navigation et redirections frontend.
- `documentation/menu.md` : menu principal.
- `documentation/about.md` : page About publique.
- `documentation/database.md` : schema PostgreSQL et migrations.
- `documentation/ci.md` : pipeline CI et publication Docker.
