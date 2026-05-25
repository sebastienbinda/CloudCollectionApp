# 01 - Rapport d'analyse du code existant

## Synthese

Le rebase sur `main` a rendu disponibles `documentation/backend-arch.md`, `documentation/frontend-arch.md` et `documentation/backend-api.md`.

Le workflow `tasks/user_collection/user_collection_workflow.md` peut etre implemente sans changement de schema obligatoire. Les tables et colonnes necessaires existent deja, notamment `t_user.collection_file_path`, `t_game.developer` et `t_user_collection`.

La suite doit principalement ajouter une configuration de taille d'upload, un montage Docker de workspace utilisateur, un lecteur ODS d'import, une normalisation dediee, des repositories SQL par entite, un service metier, deux endpoints et un workflow frontend d'onboarding/upload.

## Documentations verifiees

- `tasks/user_collection/user_collection_workflow.md` : workflow cible, endpoints et regles d'import.
- `documentation/database.md` : schema de reference et contraintes database.
- `documentation/authentication.md` : routes protegees par Bearer, profil minimal `USER`.
- `documentation/site-plan.md` : redirection des utilisateurs non authentifies vers About.
- `documentation/backend-arch.md` : `app.py` reste composition root, controleurs sous `backend/controllers/`, logique metier sous `backend/services/`.
- `documentation/frontend-arch.md` : `App.jsx` reste composition, API sous `frontend/src/services/`, orchestration sous `frontend/src/hooks/`.
- `documentation/backend-api.md` : API actuelle a completer avec les nouveaux endpoints.

## Modeles backend existants

### Utilisateur

Fichier : `backend/services/database/user.py`

Modele : `User`

Champs utiles : `id`, `email`, `profile`, `status`, `collection_file_path`, `collection_file_description`.

Conclusion : le champ `collection_file_path` existe deja et peut stocker `/users/workspace/<user_id>/<user_id>-collection.ods`.

### Plateforme

Fichier : `backend/services/database/platform.py`

Modele : `Platform`

Champs utiles : `id`, `name`, `release_date`, `manufacturer`, `description`, `status`.

Conclusion : le statut `UNKNOWN` peut etre stocke dans `status`, aucune contrainte enum n'est documentee sur `t_platform.status`.

### Studio

Fichier : `backend/services/database/studio.py`

Modele : `Studio`

Champs utiles : `id`, `name`, `country`, `city`, `creation_date`, `status`.

Conclusion : `name` est unique. Le statut `UNKNOWN` peut etre stocke dans `status`, aucune contrainte enum n'est documentee sur `t_studio.status`.

### Jeu

Fichier : `backend/services/database/game.py`

Modele : `Game`

Champs utiles : `id`, `name`, `release_date`, `developer`, `editor`, `platform`, `description`.

Conclusion : la colonne technique existante est `developer`. L'import doit mapper le champ fonctionnel `developer` du document vers `Game.developer` / `t_game.developer`.

### Association utilisateur-collection

Fichier : `backend/services/database/user_collection.py`

Modele : `UserCollection`

Champs utiles : `user_id`, `game_id`, `game_additional_name`.

Conclusion : la table d'association existe deja. `game_additional_name` peut rester `NULL` ou vide selon la convention choisie lors de l'implementation.

## Repositories et services existants

### Repository utilisateur

Fichier : `backend/services/database/user_repository.py`

Classe : `SqlAlchemyUserRepository`

Operations actuelles :

- creation utilisateur;
- recherche utilisateur;
- suppression utilisateur;
- lock/unlock;
- verification email;
- authentification utilisateur verifie;
- mise a jour de `last_connexion_date`.

Limites pour l'import :

- aucune methode actuelle ne lit `collection_file_path`;
- aucune methode actuelle ne met a jour `collection_file_path`;
- aucune methode actuelle ne gere plateformes, studios, jeux et `t_user_collection`.

Conclusion : les acces CRUD au champ `t_user.collection_file_path` doivent etre ajoutes dans `SqlAlchemyUserRepository`, car ils restent dans le domaine de persistance utilisateur. La gestion SQL des plateformes, studios et jeux ne doit pas etre ajoutee a ce repository.

### Repositories plateformes, studios et jeux

Fichiers probables :

- `backend/services/database/platform_repository.py`
- `backend/services/database/studio_repository.py`
- `backend/services/database/game_repository.py`

Conclusion : creer un repository dedie par entite pour les plateformes, studios et jeux. Ces repositories porteront les recherches par cle normalisee, les insertions si absent, et les operations necessaires a l'association via `t_user_collection` si cela reste plus coherent dans le repository jeu ou dans un repository d'association dedie.

### Service utilisateur

Fichier : `backend/services/users/user_management_service.py`

Classe : `UserManagementService`

Role actuel :

- orchestration de l'administration utilisateur.

Conclusion : ne pas y mettre l'import de collection. Le workflow d'import est un nouveau bloc metier utilisateur/collection, distinct de l'administration.

### Service jeux ODS existant

Fichier : `backend/services/games/games_service.py`

Classe : `GamesService`

Role actuel :

- lecture du fichier ODS global via `JEUXVIDEO_ODS_PATH`;
- recherche de jeux;
- ajout/modification/suppression de lignes ODS;
- lecture des plateformes;
- lecture des images;
- reset cache;
- telechargement du fichier ODS.

Conclusion : ce service doit rester centre sur l'ODS applicatif courant. Pour l'import en base, il peut inspirer la construction du lecteur ODS, mais ne doit pas recevoir toute la logique SQL d'import.

## Lecteur ODS existant a factoriser

### Fichier principal

Fichier : `backend/services/ods/ods_reader.py`

Classe : `OdsReader`

Methodes utiles :

- `list_platforms()`
- `read_games_dataframe(platform)`
- `_load_platforms()`
- `_load_games_dataframe(platform)`
- `_normalize_games_dataframe_columns(dataframe)`
- `_date_series(series)`

Comportement actuel important :

- les onglets `Accueil` et `Liste de souhaits` sont exclus des plateformes;
- les feuilles plateforme sont lues avec `header=5`;
- les colonnes sont lues en `F:M` pour les plateformes;
- les colonnes de wishlist sont lues en `F:L`;
- les variantes d'apostrophes sont normalisees pour `Date d'achat`, `Lieu d'achat`, `Prix d'achat`;
- un fallback XML existe via `OdsXmlReader.read_games_dataframe_from_xml(platform)`.

### Modele de ligne ODS

Fichier : `backend/models/jeu_video.py`

Classe : `JeuVideo`

Champs lus :

- `Nom du jeu`
- `Studio`
- `Date de sortie`
- `Date d'achat`
- `Lieu d'achat`
- `Note`
- `Prix d'achat`
- `Version`

Conclusion : pour l'import, les champs utiles sont deja identifies : `Nom du jeu`, `Studio`, `Date de sortie`. Le service d'import pourra s'appuyer sur une structure dediee plutot que reutiliser directement `JeuVideo`, car l'import SQL n'a pas besoin des champs achat/prix/version.

## Controleurs backend existants

### Composition root

Fichier : `backend/app.py`

Constat :

- `app.py` configure les logs, Flask, CORS, schema database;
- instancie les controleurs;
- enregistre les routes;
- applique `AuthGuard.protect_all_routes`.

Impact :

- ajouter seulement l'instanciation et l'enregistrement des nouveaux services/controleurs si necessaire;
- ne pas ajouter de logique d'import dans `app.py`.

### UserController

Fichier : `backend/controllers/user_controller.py`

Classe : `UserController`

Routes actuelles :

- `GET /api/users`
- `DELETE /api/users/<id>`
- `POST /api/users/<id>/lock`
- `POST /api/users/<id>/unlock`

Profil actuel :

- `ADMIN` pour l'administration utilisateur.

Impact :

- les nouveaux endpoints `/api/users/me/collection` et `/api/users/import` concernent l'utilisateur connecte avec profil `USER`;
- il est possible d'etendre `UserController`, mais il faudra separer proprement les methodes d'administration et les methodes self-service;
- alternative plus propre : creer un controleur dedie, par exemple `UserCollectionImportController`, si `UserController` devient trop heterogene.

### AuthGuard

Fichier : `backend/services/auth/auth_guard.py`

Comportement important :

- protection globale par Bearer;
- profil par defaut `USER`;
- `require_profile(minimum_profile)`;
- `validate_current_request()` valide le token mais ne retourne pas l'identite decodee au controleur.

Risque :

- pour lier l'import a l'utilisateur connecte, il faut retrouver l'identite courante. Aujourd'hui `AuthGuard.validate_current_request()` ne semble pas exposer le payload valide via `flask.g`.
- le token contient `sub` et `profile`, mais pas `id`.
- il faudra probablement rechercher l'utilisateur par email/sub, ou faire evoluer proprement `AuthGuard` pour exposer le payload valide sans dupliquer la validation du token.

## Services de configuration existants

### DatabaseConfiguration

Fichier : `backend/services/database/database_configuration.py`

Role actuel :

- lit `DATABASE_URL`, `DB_SCHEMA_NAME`, `APP_VERSION`;
- valide le schema;
- normalise l'URL PostgreSQL.

Impact :

- ne pas ajouter `USERS_WORKSPACE` ici si cette configuration n'est pas liee a la connexion database;
- ne pas lire `USERS_WORKSPACE` depuis les services backend : cette variable sert uniquement a Docker Compose pour choisir le repertoire hote monte;
- creer une configuration backend dediee uniquement pour les valeurs applicatives necessaires, notamment `USER_COLLECTION_MAX_UPLOAD_BYTES` et le chemin conteneur cible si celui-ci doit rester configurable.

### Docker Compose

Fichiers :

- `docker/docker-compose.local.yml`
- `docker/docker-compose.online.yml`

Impact attendu :

- ajouter `USERS_WORKSPACE` comme variable Docker Compose cote hote, utilisee seulement pour le volume;
- ajouter `USER_COLLECTION_MAX_UPLOAD_BYTES=104857600`;
- ajouter un volume hote vers `/users/workspace` pour le backend.

## Frontend existant

### Services API

Fichiers :

- `frontend/src/services/JeuxVideoApi.js`
- `frontend/src/services/UsersApi.js`
- `frontend/src/services/AuthApi.js`

Constat :

- `JeuxVideoApi` centralise `fetchJson`, les headers Bearer et la gestion session expiree;
- `UsersApi` est dedie a l'administration utilisateur;
- les appels proteges doivent utiliser `AuthApi.getAuthorizationHeaders()`.

Impact :

- ajouter un service dedie, par exemple `frontend/src/services/UserCollectionApi.js`, pour eviter de melanger self-service collection et administration utilisateur;
- reutiliser `JeuxVideoApi.fetchJson()` pour `GET /api/users/me/collection`;
- pour `POST /api/users/import`, utiliser `fetch` avec `FormData` sans header `Content-Type` manuel, mais avec `Authorization`.

### View-model principal

Fichier : `frontend/src/hooks/app/useCloudCollectionViewModel.js`

Role actuel :

- assemble les hooks metier;
- fournit `viewProps` a `AppViewSwitch`;
- gere session, navigation, home, plateformes, jeux, wishlist.

Impact :

- ajouter un hook de domaine pour le workflow collection utilisateur, probablement sous `frontend/src/hooks/collection/` ou `frontend/src/hooks/userCollection/`;
- ne pas mettre l'appel API directement dans `App.jsx`;
- eviter de gonfler `useCloudCollectionViewModel.js` en deleguant l'etat d'onboarding/import a un hook dedie.

### Navigation

Fichiers :

- `frontend/src/hooks/navigation/useAppNavigation.js`
- `frontend/src/appRouting.js`
- `frontend/src/components/AppViewSwitch.jsx`

Constat :

- les vues actuelles sont `about`, `auth`, `home`, `games`, `addGame`, `adminDashboard`, `users`, `wishlist`;
- `/accueil` est la page home authentifiee;
- les utilisateurs non authentifies sont rediriges vers `/about`.

Impact :

- ajouter une vue dediee, par exemple `collectionImport`;
- ajouter une route frontend, par exemple `/collection/import`;
- apres connexion, si `has_collection=false`, rediriger vers cette vue;
- si `has_collection=true`, conserver la redirection actuelle vers `/accueil`.

## Tests existants a completer

### Backend routes

Fichier : `backend/tests/test_app_routes.py`

Le fichier contient deja les fakes de repository/configuration et les tests des routes authentifiees, utilisateurs admin, ODS jeux et wishlist. Tests a ajouter :

- `GET /api/users/me/collection` sans token -> `403`;
- `GET /api/users/me/collection` avec token valide et collection absente -> `200` avec `has_collection=false`;
- `GET /api/users/me/collection` avec collection presente -> `200` avec `has_collection=true`;
- `POST /api/users/import` sans token -> `403`;
- `POST /api/users/import` sans fichier -> `400`;
- `POST /api/users/import` fichier trop volumineux -> `413`;
- `POST /api/users/import` collection deja importee -> `409`;
- `POST /api/users/import` succes -> `201` avec compteurs.

### Backend ODS

Fichier : `backend/tests/test_ods_reader.py`

Tests a ajouter ou completer :

- extraction des feuilles plateforme importables;
- rejet d'un fichier sans feuille plateforme;
- rejet d'une feuille plateforme sans colonnes requises;
- lecture de `Nom du jeu`, `Studio`, `Date de sortie`;
- date vide ou invalide -> `None` et warning.

### Backend services

Fichiers probables a creer :

- `backend/tests/test_user_collection_import_service.py`
- tests repositories par entite ou tests avec fakes selon les conventions retenues;
- `backend/tests/test_user_collection_normalization.py`

### Frontend

Pas de structure de tests frontend visible dans l'analyse rapide. Validation minimale attendue :

- `npm run build` depuis `frontend/`;
- verification manuelle du workflow si aucun test frontend n'existe.

## Nouveaux fichiers probablement necessaires

### Backend

Noms indicatifs a confirmer pendant l'implementation :

- `backend/services/users/user_collection_status_service.py` ou service equivalent pour `has_collection`;
- `backend/services/users/user_collection_import_service.py`;
- `backend/services/users/user_collection_import_configuration.py`;
- `backend/services/users/user_collection_import_models.py`;
- `backend/services/users/user_collection_name_normalizer.py`;
- `backend/services/database/platform_repository.py`;
- `backend/services/database/studio_repository.py`;
- `backend/services/database/game_repository.py`;
- `backend/services/ods/ods_collection_import_reader.py`;
- tests associes sous `backend/tests/`.
- `backend/controllers/user_collection_import_controller.py`
  ou extension de `backend/controllers/user_controller.py` si le fichier reste clair.

### Frontend

Noms indicatifs :

- `frontend/src/services/UserCollectionApi.js`;
- `frontend/src/hooks/collection/useUserCollectionImportWorkflow.js`;
- `frontend/src/components/UserCollectionImportView.jsx`;
- style dedie sous `frontend/src/styles/` si necessaire.

## Fichiers existants a modifier probablement

### Backend

- `backend/app.py` : enregistrer le controleur si un nouveau controleur est cree.
- `backend/controllers/user_controller.py` : ajouter les endpoints si aucun controleur dedie n'est cree.
- `backend/controllers/__init__.py` : exporter le nouveau controleur si applicable.
- `backend/services/__init__.py` : exporter les nouveaux services si le projet continue cette convention.
- `backend/services/database/__init__.py` : exporter le nouveau repository si applicable.
- `docker/docker-compose.local.yml` : ajouter workspace et variables.
- `docker/docker-compose.online.yml` : ajouter workspace et variables.
- `documentation/backend-api.md` : ajouter les endpoints.
- `README.md` : verifier la section configuration/Docker.

### Frontend

- `frontend/src/hooks/app/useCloudCollectionViewModel.js` : brancher le hook d'import.
- `frontend/src/hooks/navigation/useAppNavigation.js` : ajouter la navigation vers la vue d'import.
- `frontend/src/appRouting.js` : ajouter la route frontend si une route dediee est choisie.
- `frontend/src/components/AppViewSwitch.jsx` : rendre la nouvelle vue.
- `frontend/src/components/MainMenu.jsx` : verifier si la vue doit cacher ou conserver certaines actions pendant l'onboarding.

## Risques et points d'attention

### Identite utilisateur connecte

Le token ne contient pas `id`, seulement `sub` et `profile`. Le service d'import doit obtenir l'utilisateur courant sans dupliquer la validation Bearer dans le controleur.

Option recommandee :

- faire exposer par `AuthGuard` le payload valide dans `flask.g`, ou ajouter un helper controle pour lire l'identite deja validee;
- rechercher ensuite l'utilisateur par email/sub via repository.

### Atomicite DB et fichier

La transaction SQL doit etre atomique, mais le fichier copie n'est pas transactionnel. Il faudra :

- copier dans un chemin final ou temporaire selon l'approche retenue;
- supprimer le fichier en cas d'echec;
- ne mettre a jour `collection_file_path` qu'en fin de succes.

### Normalisation vs contraintes uniques

La base a des contraintes uniques sensibles aux accents et a la casse :

- `t_studio.name`;
- `t_game(name, platform)`.

La comparaison metier doit donc rechercher les equivalents normalises avant insertion pour eviter de creer des doublons fonctionnels que la base accepterait techniquement.

### `Platform.name` sans contrainte unique documentee

`t_platform.name` n'a pas de contrainte unique documentee. Le repository d'import devra explicitement chercher les plateformes existantes par cle normalisee avant insertion.

### Taille des fichiers

La validation `USER_COLLECTION_MAX_UPLOAD_BYTES` doit eviter de charger inutilement un fichier trop volumineux en memoire si possible.

### Type MIME ODS

Le controle du type ne doit pas reposer uniquement sur le MIME fourni par le navigateur. Il faut au minimum verifier extension `.ods` et lisibilite comme ODS.

### Documentation

Ajouter les endpoints modifiera l'API documentee. `documentation/backend-api.md` devra etre mis a jour pendant les taches d'implementation.

Ajouter une nouvelle route frontend ou changer la redirection post-login concerne `documentation/site-plan.md`. Selon `AGENTS.md`, toute modification contradictoire ou ajout fonctionnel documente doit etre proposee avant modification documentaire.

## Ordre conseille pour la suite

1. Tache 02 : configuration backend et Docker.
2. Tache 03 : lecteur ODS dedie a l'import.
3. Tache 04 : normalisation et deduplication.
4. Tache 05 : service et repository d'import.
5. Tache 06 : endpoints backend.
6. Taches 07 et 08 : API frontend puis onboarding.
7. Taches 09 et 10 : documentation et validation end-to-end.
