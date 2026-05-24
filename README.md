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

Application web personnelle qui transforme un fichier de collection LibreOffice
Calc `.ods` en site en ligne accessible a tout moment. Chaque utilisateur garde
sa collection privee rattachee a son compte, tout en contribuant a enrichir une
base commune de jeux, plateformes et studios.

Le fichier ODS importe initialise la collection personnelle. Le backend expose
une API securisee pour proteger les donnees utilisateur et alimenter le
referentiel commun, tandis que le frontend fournit une interface web de
consultation, recherche, import et edition.

## Fonctionnalites

- Tableau de bord de collection avec statistiques par plateforme.
- Bibliotheque publique des plateformes, studios et jeux du referentiel commun.
- Navigation par plateforme et consultation d'une liste de souhaits.
- Recherche globale par nom de jeu.
- Filtres, tris, ajout, modification et suppression de jeux apres authentification.
- Import de collection ODS personnelle pour les utilisateurs inscrits.
- Page About publique, authentification Bearer et creation de compte avec validation email.
- Administration utilisateur, telechargement ODS et reset du cache.
- Sauvegarde automatique du fichier ODS avant chaque ecriture.
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
- pandas, odfpy et XML/ZIP standard library pour le fichier ODS

Organisation :

- `backend/app.py` : composition Flask, initialisation runtime, enregistrement des controllers et protection globale.
- `backend/controllers/` : endpoints HTTP et mapping des reponses.
- `backend/services/` : services metier et infrastructure organises par domaine.
- `backend/services/ods/` : lecture, ecriture, backup, cache et validation ODS.
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
- `hooks/collection/` : rechargement transversal, reset cache ODS et onboarding d'import.
- `hooks/home/` : accueil, images protegees et recherche globale.
- `hooks/library/` : Bibliotheque publique, recherche, tri et pagination serveur.
- `hooks/platforms/` : catalogue de plateformes.
- `hooks/games/` : collection plateforme, tri, filtres et ajout.
- `hooks/wishlist/` : actions liste de souhaits.

Regles detaillees :

- Architecture frontend : `documentation/frontend-arch.md`
- Plan de navigation : `documentation/site-plan.md`
- Menu : `documentation/menu.md`
- Page About : `documentation/about.md`

## Configuration ODS

Le backend ne contient aucun chemin ODS code en dur.

Variables principales :

- `JEUXVIDEO_ODS_PATH` : chemin du fichier ODS pour un lancement backend direct.
- `JEUXVIDEO_ODS_FILE` : fichier ODS monte par Docker Compose.
- `JEUXVIDEO_ODS_BACKUP_DIR` : repertoire des sauvegardes.
- `JEUXVIDEO_ODS_TMP_DIR` : repertoire temporaire d'ecriture.
- `ODS_FORMULA_RECALCULATION` : politique de recalcul des formules.
- `USERS_WORKSPACE` : repertoire hote monte par Docker Compose dans `/users/workspace`.
- `USER_COLLECTION_MAX_UPLOAD_BYTES` : taille maximale d'upload d'une collection
  utilisateur, appliquee a Flask et au proxy Nginx du service `web`.

Un fichier exemple versionnable est fourni :

```text
collection-example.ods
```

Structure fonctionnelle attendue :

- onglet `Accueil` pour les statistiques;
- onglet `Liste de souhaits`;
- un onglet par plateforme.

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

Services locaux :

- application : `http://localhost:8080`
- Mailpit : `http://localhost:8025`

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
JEUXVIDEO_ODS_PATH=../collection-example.ods BACKEND_PORT=7777 python app.py
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

Documentation CI : `documentation/ci.md`.

## Documentation

Documents fonctionnels et techniques principaux :

- `documentation/backend-api.md` : routes et contrats API backend.
- `documentation/backend-arch.md` : architecture Flask/backend.
- `documentation/frontend-arch.md` : architecture React/Vite.
- `documentation/authentication.md` : authentification, routes protegees et session frontend.
- `documentation/import.md` : regles fonctionnelles d'import de collection utilisateur.
- `documentation/register.md` : inscription utilisateur et validation email.
- `documentation/users.md` : administration des utilisateurs.
- `documentation/site-plan.md` : navigation et redirections frontend.
- `documentation/menu.md` : menu principal.
- `documentation/about.md` : page About publique.
- `documentation/database.md` : schema PostgreSQL et migrations.
- `documentation/ci.md` : pipeline CI et publication Docker.
