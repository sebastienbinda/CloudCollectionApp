# 00 - Resultat d'analyse du code existant et architecture proposee

## Perimetre

Cette analyse couvre la tache `plateforme_list` sans modification de code
applicatif. Elle sert de contrat de travail pour les sous-taches suivantes.

Documents lus :

- `tasks/0.2.6/plateforme_list/plateforme_list.md`
- `documentation/database.md`
- `documentation/import.md`
- `documentation/backend-api.md`
- `documentation/backend-arch.md`
- `documentation/frontend-arch.md`
- `documentation/site-plan.md`
- `documentation/authentication.md`

## Cartographie Backend

### Schema et migrations

- Modele ORM : `backend/services/database/platform.py`
  - Classe `Platform`.
  - Colonnes actuelles : `id`, `name`, `release_date`, `manufacturer`,
    `description`, `status`.
  - `release_date` et `manufacturer` sont actuellement nullable.
  - `status` est actuellement non nullable.
- Migration initiale : `backend/migrations/versions/20260522_0004_create_database_schema.py`
  - Cree `t_platform` avec `status`.
  - Cree `t_game` avec FK `platform -> t_platform.id`.
  - Ne doit pas etre modifiee directement : elle existe dans des tags publies
    (`0.2.0` a `0.2.4`) et `documentation/database.md` impose
    l'immutabilite des migrations publiees.
- Service d'initialisation : `backend/services/database/database_schema_service.py`
  - Applique Alembic au demarrage via `DatabaseSchemaService`.
  - C'est le bon point d'orchestration infrastructure, pas le bon endroit pour
    mettre des regles metier de matching.

### Repositories plateformes

- `backend/services/database/platform_repository.py`
  - `load_ids_by_key()` charge les plateformes par cle normalisee.
  - `insert()` cree aujourd'hui une plateforme avec `status = UNKNOWN`.
  - `list_public_library_platforms()` retourne `status` et ne retourne pas
    `end_date`.
  - Les tris Bibliotheque autorises sont `name`, `release_date`,
    `manufacturer`.
- `backend/services/database/user_collection_query_repository.py`
  - `list_platforms()` retourne seulement `id`, `name`, `nb_games`.
  - Le endpoint collection ne peut donc pas encore afficher `release_date` /
    `end_date`.
  - `PLATFORM_SORT_COLUMNS` ne supporte que `name`.

### Import utilisateur

- Controller : `backend/controllers/user_collection_import_controller.py`
  - `POST /api/users/import` retourne `UserCollectionImportResult.to_dict()`.
  - Les routes sont protegees avec `AuthGuard.require_profile(USER)`.
  - Le blocage pendant reset Bibliotheque est deja gere.
- Service : `backend/services/users/user_collection_import_service.py`
  - `UserCollectionImportResult` expose `created_platforms`,
    `created_studios`, `created_games`, `associated_games`,
    `wishlisted_games`, `warnings`.
  - `_map_result()` copie `persistence_result.created_platforms`.
- Repository transactionnel :
  `backend/services/database/user_collection_import_repository.py`
  - `UserCollectionImportPersistenceResult` expose `created_platforms`.
  - `_ensure_platforms()` cree les plateformes absentes pendant l'import.
  - `_ensure_games()` suppose que chaque plateforme de jeu existe dans
    `platform_ids`; si une plateforme n'est pas trouvee apres changement de
    comportement, ce code doit eviter un `KeyError` non fonctionnel.
- Modeles d'import :
  `backend/services/collection/imports/collection_import_models.py`
  - `CollectionImportData.platforms` contient les plateformes lues.
  - `CollectionImportGame.platform_name` porte le nom de plateforme brut.
  - `CollectionImportWarnings` contient aujourd'hui `invalid_wishlist`,
    `invalid_wishlist_values_found`, `invalid_games`.

### Normalisation et recherche

- Normaliseur existant :
  `backend/services/users/user_collection_name_normalizer.py`
  - `comparison_key()` fait `trim().lower()` et supprime les accents.
  - Il ne supprime pas les espaces internes.
  - Il ne fait pas de fuzzy matching.
- Les filtres SQL de collection et Bibliotheque utilisent `TRANSLATE(LOWER(...))`
  pour neutraliser casse et accents.

### Bibliotheque publique

- Controller : `backend/controllers/platform_controller.py`
  - `GET /api/library/entities`
  - `GET /api/library/platforms`
  - Routes publiques documentees.
- Service : `backend/services/library/library_service.py`
  - `_platform_payload()` retourne `id`, `name`, `release_date`,
    `manufacturer`, `description`, `status`, `total_games`.
  - Doit ajouter `end_date` et retirer `status` si le schema cible le supprime.
- Contrat documente : `documentation/backend-api.md`
  - Liste plateformes documentee avec `status`, sans `end_date`.

### Email administrateur

- Configuration existante :
  - `ADMIN_NOTIFICATION_EMAIL` est deja documente dans `README.md`.
  - Compose local et online exposent deja `ADMIN_NOTIFICATION_EMAIL`.
- Infrastructure existante :
  - `backend/services/email/email_configuration.py`
  - `backend/services/email/email_sender.py`
  - `EmailSenderFactory.create(EmailConfiguration.from_environment())`
- Exemples a reutiliser :
  - `backend/services/library/library_reset_service.py`
  - `backend/controllers/authentication_controller.py`
  - `backend/controllers/user_controller.py`

### Configuration applicative

- Les configurations existantes suivent le pattern `from_environment()`, par
  exemple :
  - `backend/services/email/email_configuration.py`
  - `backend/services/users/user_collection_import_configuration.py`
  - `backend/services/database/database_configuration.py`
- La configuration des seuils de matching doit suivre le meme pattern pour
  rester testable et injectable.

## Cartographie Frontend

### Services API

- `frontend/src/services/LibraryApi.js`
  - `fetchPlatforms()` consomme `/api/library/platforms`.
  - `buildListUrl()` transmet `name`, `platform`, `page`, `size`, `sort`.
- `frontend/src/services/VideoGamesApi.js`
  - `fetchPlatforms()` consomme
    `/collections/videogames/platforms/search?wishlist=false`.
  - `normalizeCollectionPlatforms()` transforme les plateformes collection en
    `{id, name, games_count, total_price, average_price}`.
  - Ne conserve pas `release_date`, `end_date` ni `manufacturer`.
- `frontend/src/services/UserCollectionApi.js`
  - `importCollection()` consomme le resultat de `POST /api/users/import`.
  - Les erreurs sont typees, mais les warnings restent dans le payload brut.

### Hooks

- `frontend/src/hooks/library/useLibraryPlatforms.js`
  - Colonnes actuelles : `name`, `release_date`, `manufacturer`, `status`,
    `total_games`.
  - Colonnes mobiles : `name`, `total_games`.
  - Doit remplacer `status` par `end_date` et ajuster le mobile.
- `frontend/src/hooks/library/useLibraryEntityList.js`
  - Gere recherche, tri backend et pagination.
  - Peut supporter de nouvelles colonnes sans changement majeur.
- `frontend/src/hooks/platforms/usePlatformsCatalog.js`
  - Charge les plateformes collection via `VideoGamesApi.fetchPlatforms()`.
  - Initialise la plateforme selectionnee depuis l'URL ou la premiere
    plateforme disponible.

### Composants

- `frontend/src/components/LibraryEntityListView.jsx`
  - Affiche les listes Bibliotheque via `TableComponent`.
  - Pas de rendu carte specifique aux plateformes.
- `frontend/src/components/TableComponent.jsx`
  - Utilise `mobileVisibleColumns` pour le rendu mobile.
  - Un rendu mobile strict "nom premiere ligne, release/end deuxieme ligne"
    peut etre obtenu soit par colonnes mobiles dediees, soit par un rendu custom
    additionnel si le tableau existant ne suffit pas.
- `frontend/src/components/UserCollectionOnboardingView.jsx`
  - `ImportSummary` affiche encore "Plateformes creees" depuis
    `result.created_platforms`.
  - Doit afficher "Plateformes liees" depuis le nouveau compteur.
  - `InvalidImportedGamesList` peut etre reutilise ou generalise pour les
    warnings de plateformes incertaines.
- `frontend/src/components/HomeView.jsx`
  - Cartes "Ma collection" affichent plateformes de collection avec nombre de
    jeux et stats financieres.
  - Pas directement demande par la tache, sauf si le nouveau format collection
    enrichit ces cartes.

## Architecture Cible Proposee

### Schema `t_platform`

Creer une nouvelle migration Alembic, par exemple :

```text
backend/migrations/versions/20260614_0008_platform_catalog_schema.py
```

Changements proposes :

- ajouter `end_date TIMESTAMP NULL` ;
- conserver `release_date TIMESTAMP NULL` et `manufacturer VARCHAR(128) NULL`,
  car le CSV contient des valeurs `Inconnue` et la tache demande de les stocker
  a `NULL` ;
- supprimer `status` seulement apres adaptation de tous les SELECT, payloads,
  tests et documentation ;
- ne pas modifier `20260522_0004_create_database_schema.py`.

Decision recommandee : migration idempotente et non destructive par defaut.
Elle doit charger les plateformes manquantes depuis le CSV sans vider
`t_game` ni `t_platform`, sauf confirmation explicite contraire, car
`documentation/database.md` interdit les migrations forward qui exigent un
reset de production.

### Chargement CSV

Creer un service dedie sous `backend/services/database/`, par exemple :

```text
backend/services/database/platform_catalog_seed_service.py
```

Classes proposees :

- `PlatformCatalogCsvReader`
  - lit `tasks/0.2.6/plateforme_list/consoles_jeux_video.csv` ;
  - valide les colonnes ;
  - parse les dates ;
  - retourne des objets metier simples.
- `PlatformCatalogSeedService`
  - insere ou met a jour les plateformes par cle normalisee ;
  - reste utilisable depuis une migration ou depuis un test d'infrastructure.

Mapping :

- `nom_machine` -> `t_platform.name`
- `nom_fabricant` -> `t_platform.manufacturer`
- `date_mise_en_vente` -> `t_platform.release_date`
- `date_retrait_vente` -> `t_platform.end_date`
- `description` -> `{}` ou `NULL`, a fixer en sous-tache 01.

Regles de dates recommandees :

- `YYYY-MM-DD` -> date exacte ;
- `YYYY-MM` -> premier jour du mois ;
- `YYYY` -> 1er janvier de l'annee ;
- `Inconnue` -> `NULL` ;
- `En vente` -> `NULL` pour `end_date`.

### Matching plateforme pendant l'import

Creer un service metier sous `backend/services/users/`, par exemple :

```text
backend/services/users/platform_import_matching_service.py
```

Classes proposees :

- `PlatformImportCandidate`
- `PlatformImportMatch`
- `PlatformImportMatchingConfiguration`
- `PlatformImportMatchingService`

Responsabilites :

- charger les plateformes existantes via le repository ;
- construire plusieurs cles :
  - cle normalisee actuelle ;
  - cle compacte sans espaces, tirets, underscores, ponctuation simple ;
- calculer un score de similarite pour les coquilles.

Algorithme recommande sans nouvelle dependance :

- utiliser `difflib.SequenceMatcher` de la bibliotheque standard ;
- exprimer le score en pourcentage entier de `0` a `100` ;
- score exact normalise ou compact : `100%` ;
- score fuzzy : ratio entre cle compacte importee et cle compacte reference,
  converti en pourcentage.

Seuils imposes par la tache chapeau :

- `100%` : match parfait, import sans warning plateforme ;
- `75% <= score < 100%` : match suffisamment fiable, import sans warning
  plateforme sauf ambiguite ;
- `25% <= score < 75%` : match faible, import avec warning de retour,
  verification manuelle et email administrateur ;
- `0% < score < 25%` : score vraiment trop faible, pas d'import du jeu et
  warning dans le contexte d'import ;
- `0%` : match inexistant, pas d'import du jeu et warning dans le contexte
  d'import.

Les seuils `25%` et `75%` sont les valeurs par defaut et doivent etre
configurables via variables d'environnement :

- `MATCHING_LOW_LVL_RATING`, defaut `25` ;
- `MATCHING_HIGH_LEVEL_RATING`, defaut `75`.

Configuration recommandee :

```text
backend/services/users/platform_import_matching_configuration.py
```

Classe proposee :

- `PlatformImportMatchingConfiguration`
  - `low_level_rating: int`
  - `high_level_rating: int`
  - `from_environment()`
  - `validate()`

Regles de validation recommandees :

- les valeurs doivent etre des entiers ;
- `0 <= MATCHING_LOW_LVL_RATING < MATCHING_HIGH_LEVEL_RATING <= 100` ;
- une configuration invalide doit lever `ValueError` avec un message explicite ;
- les valeurs absentes utilisent les defauts `25` et `75`.

En cas d'egalite entre deux plateformes candidates au meilleur score, traiter le
cas comme ambigu : ne pas rattacher automatiquement sans warning, envoyer l'email
administrateur et appliquer la regle de tranche du score.

### Comportement sous seuil

Decision mise a jour selon la tache chapeau :

- `score >= high_level_rating` : rattacher et importer ;
- `low_level_rating <= score < high_level_rating` : rattacher et importer, mais ajouter un warning et
  notifier l'administrateur pour verification manuelle ;
- `score < low_level_rating` ou `score = 0%` : ne pas importer les jeux concernes, ajouter
  un warning dans le contexte d'import et notifier l'administrateur si une
  action manuelle est utile.

Raison :

- `t_game.platform` est obligatoire ;
- creer une plateforme inconnue contredit la tache ;
- la tache autorise explicitement le rattachement faible avec warning entre
  25% et 75%, mais demande de bloquer l'import quand le score est vraiment trop
  faible.

Warnings proposes dans `CollectionImportWarnings.to_dict()` :

```json
{
  "invalid_wishlist": 0,
  "invalid_wishlist_values_found": [],
  "invalid_games": [],
  "unmatched_platforms": [
    {
      "platform_name": "Playstion 2",
      "best_match": "PlayStation 2",
      "score": 68,
      "action": "imported_with_manual_review",
      "games": ["Nom du jeu"]
    }
  ],
  "unimported_games": [
    {
      "name": "Nom du jeu non importe",
      "platform_name": "Plateforme inconnue",
      "best_match": "",
      "score": 0,
      "reason": "platform_match_missing"
    }
  ]
}
```

Les jeux non importes pour score `< 25%` ou `0%` doivent etre visibles dans un
champ dedie (`unimported_games` recommande) et peuvent aussi etre ajoutes a
`invalid_games` avec `field = platform` pour compatibilite UI.

### Email administrateur

Creer un service sous `backend/services/users/`, par exemple :

```text
backend/services/users/platform_import_warning_notifier.py
```

Responsabilites :

  - recevoir la liste des plateformes a verifier manuellement, non importees ou
    ambigues ;
- lire `ADMIN_NOTIFICATION_EMAIL` ;
- envoyer via `EmailSender` injecte ;
- ne pas faire echouer l'import si l'email echoue, sauf decision contraire.

Factory :

- injecter par defaut `EmailSenderFactory.create(EmailConfiguration.from_environment())`.
- reprendre le style de `LibraryResetService`.

Sujet propose :

```text
CloudCollectionApp - Verification manuelle de plateformes importees
```

Corps minimal :

- utilisateur concerne si disponible ;
- plateforme fournie ;
- meilleure suggestion ;
- score en pourcentage ;
- action retenue : importe, importe avec verification manuelle, non importe ;
- liste des jeux impactes.

### Resultat d'import

Renommer fonctionnellement le compteur :

- nouveau champ recommande : `linked_platforms`.
- calcul : nombre de plateformes distinctes du referentiel associees aux jeux
  effectivement importes ou reutilises.
- conserver temporairement `created_platforms` avec valeur `0` uniquement si
  l'analyse de compatibilite frontend le demande. Sinon, supprimer du contrat
  et mettre a jour tous les tests.

Changements backend :

- `UserCollectionImportPersistenceResult`
- `UserCollectionImportResult`
- `UserCollectionImportResult.to_dict()`
- `SqlAlchemyUserCollectionImportRepository.import_collection()`
- tests route/service.

### API plateformes

Format cible recommande pour `/api/library/platforms` :

```json
{
  "id": 1,
  "name": "PlayStation 2",
  "release_date": "2000-03-04",
  "end_date": "2013-01-04",
  "manufacturer": "Sony Computer Entertainment",
  "description": {},
  "total_games": 42
}
```

Format cible recommande pour `/collections/videogames/platforms/search` :

```json
{
  "id": 1,
  "name": "PlayStation 2",
  "release_date": "2000-03-04",
  "end_date": "2013-01-04",
  "manufacturer": "Sony Computer Entertainment",
  "nb_games": 12
}
```

Modifications backend :

- `SqlAlchemyPlatformRepository.LIBRARY_SORT_COLUMNS` : ajouter `end_date`.
- `SqlAlchemyPlatformRepository.list_public_library_platforms()` : SELECT et
  GROUP BY `end_date`, retirer `status` si supprime.
- `LibraryService._platform_payload()` : ajouter `end_date`, retirer `status`.
- `SqlAlchemyUserCollectionQueryRepository.list_platforms()` : SELECT
  `release_date`, `end_date`, `manufacturer`.
- `UserCollectionQueryService._platform_payload()` : exposer les nouveaux
  champs.

### Frontend

Modifications recommandees :

- `frontend/src/hooks/library/useLibraryPlatforms.js`
  - colonnes : `name`, `release_date`, `end_date`, `manufacturer`,
    `total_games` ;
  - retirer `status` ;
  - rendre mobile : `name`, `release_date`, `end_date` ou une colonne
    composee si besoin.
- `frontend/src/services/VideoGamesApi.js`
  - conserver `release_date`, `end_date`, `manufacturer` dans
    `normalizeCollectionPlatforms()`.
- `frontend/src/components/UserCollectionOnboardingView.jsx`
  - remplacer "Plateformes creees" par "Plateformes liees" ;
  - lire `result.linked_platforms` ;
  - afficher `warnings.unmatched_platforms` dans une section dediee.
- `frontend/src/components/TableComponent.jsx`
  - a modifier seulement si le rendu mobile exige une ligne composee
    impossible avec `mobileVisibleColumns`.

## Tests À Créer Ou Modifier

### Backend

Tests existants a adapter :

- `backend/tests/test_user_collection_import_service.py`
- `backend/tests/test_user_collection_routes.py`
- `backend/tests/test_user_collection_import_wishlist_result.py`
- `backend/tests/test_library_service.py`
- `backend/tests/test_library_routes.py`
- `backend/tests/test_library_entity_repositories.py`
- `backend/tests/test_user_collection_query_service.py`
- `backend/tests/test_user_collection_query_repository.py`
- `backend/tests/route_test_support.py`

Tests nouveaux recommandes :

- `backend/tests/test_platform_catalog_csv_reader.py`
- `backend/tests/test_platform_catalog_seed_service.py`
- `backend/tests/test_platform_import_matching_service.py`
- `backend/tests/test_platform_import_warning_notifier.py`

Cas minimum :

- CSV valide ;
- `Inconnue` -> `NULL` ;
- `En vente` -> `NULL` pour `end_date` ;
- chargement idempotent ;
- matching exact ;
- casse differente ;
- accents differents ;
- espaces differents ;
- coquille acceptee ;
- score entre 25% et 75% avec import, warning et email ;
- score inferieur a 25% sans import ;
- score a 0% sans import ;
- seuils par defaut lus depuis l'absence de variables d'environnement ;
- seuils personnalises via `MATCHING_LOW_LVL_RATING` et
  `MATCHING_HIGH_LEVEL_RATING` ;
- refus d'une configuration non numerique ;
- refus d'une configuration hors bornes `0..100` ;
- refus d'une configuration avec seuil bas superieur ou egal au seuil haut ;
- ambiguite ;
- warning avec jeux impactes ;
- email admin appele ;
- aucune creation de plateforme pendant l'import ;
- compteur `linked_platforms`.

### Frontend

Il n'y a pas de suite de tests frontend evidente dans les fichiers inspectes.
Validation minimale :

- `npm run build` depuis `frontend/`.
- Verification manuelle hors `iab` si le navigateur integre reste indisponible,
  conformement a `AGENTS.md`.

## Risques Identifiés

- Suppression de `status` : plusieurs payloads, tests et docs le referencent.
- Nullabilite : la tache chapeau indique `release_date` et `manufacturer` non
  null, mais demande aussi `NULL` quand le CSV contient `Inconnue`.
- Migration destructive : vider `t_game` et `t_platform` contredit
  `documentation/database.md`.
- Fuzzy matching : risque de faux positif, surtout dans la tranche 25% a 75%
  qui importe avec warning et verification manuelle.
- Import partiel : si des jeux sont ignores faute de plateforme fiable, les
  compteurs doivent rester coherents.
- Email admin : l'envoi ne doit pas bloquer toute la transaction si SMTP est
  temporairement indisponible, sauf decision explicite.
- Configuration des seuils : des valeurs `.env` invalides peuvent bloquer
  l'import. Le message d'erreur doit etre explicite pour faciliter
  l'exploitation.
- CSV volumineux en migration : privilegier un service testable et un appel
  idempotent plutot que du SQL inline difficile a maintenir.

## Decisions Proposées Pour Les Sous-Tâches

1. Ne pas modifier les migrations publiees.
2. Ne pas vider `t_game` ni `t_platform` sans confirmation explicite.
3. Ajouter `end_date`.
4. Supprimer `status` dans une migration corrective seulement si tous les
   consommateurs sont adaptes dans le meme chantier.
5. Garder `release_date` et `manufacturer` nullable pour respecter les valeurs
   inconnues du CSV.
6. Ne plus creer de plateformes pendant l'import.
7. Utiliser un matching exact normalise, puis compact, puis fuzzy avec
   `difflib.SequenceMatcher`.
8. Appliquer les seuils de la tache avec defauts `100%`, `75%`, `25%`, `0%`.
9. Rendre les seuils bas et haut configurables via `MATCHING_LOW_LVL_RATING`
   et `MATCHING_HIGH_LEVEL_RATING`.
10. Importer avec warning et email entre le seuil bas et le seuil haut.
11. Ne pas importer les jeux avec score inferieur au seuil bas ou score a `0%`.
12. Retourner `linked_platforms` dans le resultat d'import.
13. Envoyer les alertes a `ADMIN_NOTIFICATION_EMAIL` via l'infrastructure email
    existante.

## Points À Confirmer Avant Implémentation

- Confirmer que la migration ne doit plus vider `t_game` et `t_platform`.
- Confirmer que `status` doit bien disparaitre du schema et de l'API.
- Confirmer que `release_date` et `manufacturer` peuvent rester nullable.

Interpretation retenue des bornes de seuil :

- `75%` n'est pas `< 75%`, donc entre dans la tranche import sans warning
  plateforme ;
- `25%` n'est pas `< 25%`, donc entre dans la tranche import avec warning,
  verification manuelle et email administrateur.

## Documentation À Mettre À Jour En Dernier

- `README.md`
- `documentation/database.md`
- `documentation/import.md`
- `documentation/backend-api.md`
- `documentation/backend-arch.md` si nouveaux services structurants.
- `documentation/frontend-arch.md` si hooks/services frontend changent.
- `documentation/site-plan.md` si le rendu ou comportement des pages change.
- Docker compose local / online si les nouvelles variables de seuil doivent
  etre exposees explicitement.

## Validations À Prévoir

- Tests backend cibles pendant chaque sous-tache.
- `./test_backend.sh` apres modifications backend.
- `npm run build` depuis `frontend/` apres modifications frontend.
- `docker compose -f docker/docker-compose.local.yml build backend web` si les
  changements impactent le runtime.
- `git diff --check`.
