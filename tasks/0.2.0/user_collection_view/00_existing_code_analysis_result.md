# 00 - Rapport d'analyse du code existant

## Synthèse

Le fonctionnement actuel de consultation de collection est encore centré sur le
fichier ODS global résolu par `JEUXVIDEO_ODS_PATH`. Les routes backend de
collection, de plateformes, de wishlist et plusieurs hooks frontend passent par
`GamesService`, qui instancie `OdsPathResolver`, `OdsCache`, `OdsReader`,
`OdsImageReader` et `OdsXmlReader`. L'ancien writer ODS a ete supprime apres le
retrait des actions d'ecriture ODS.

Le workflow d'import utilisateur existe déjà et persiste les plateformes,
studios, jeux et associations dans PostgreSQL. Les tables nécessaires à la
consultation SQL existent : `t_user`, `t_user_collection`, `t_game`,
`t_platform` et `t_studio`.

L'architecture cible peut être développée sans migration de schéma obligatoire.
Le travail principal consiste à remplacer les lectures ODS de consultation par
une lecture SQL filtrée par utilisateur connecté, supprimer la wishlist, retirer
les routes ODS hors import et adapter le frontend.

## Documentations relues

- `tasks/user_collection_view/user_collection_view.md` : objectif fonctionnel,
  endpoints cibles, endpoints à supprimer et suppression wishlist.
- `tasks/user_collection_view/01_contract_and_scope.md` à
  `tasks/user_collection_view/07_cleanup_documentation_validation.md` :
  découpage et critères de validation.
- `documentation/backend-api.md` : catalogue API actuel et comportement des
  routes existantes.
- `documentation/backend-arch.md` : contrôleurs sous `backend/controllers/`,
  services métier sous `backend/services/`, repositories sous
  `backend/services/database/`.
- `documentation/frontend-arch.md` : appels HTTP dans `frontend/src/services/`,
  orchestration dans `frontend/src/hooks/`, composants centrés rendu.
- `documentation/database.md` : contrat des tables `t_user`,
  `t_user_collection`, `t_game`, `t_platform`, `t_studio`.
- `documentation/authentication.md` : routes protégées par Bearer et profil
  minimal `USER`.
- `documentation/site-plan.md` et `documentation/menu.md` : navigation et routes
  frontend à maintenir cohérentes.

## Cartographie des endpoints actuels

| Endpoint | Méthode | Controller actuel | Source actuelle | Décision |
| --- | --- | --- | --- | --- |
| `/collections/videogames/search` | `GET` | `UserGamesCollectionController` | ODS via `GamesService.search` | Supprimer |
| `/collections/videogames/home` | `GET` | `UserGamesCollectionController` | ODS `Accueil` via `GamesService.get_home_stats` | Remplacer par `GET /collections/videogames` |
| `/collections/videogames/cache/reset` | `POST` | `UserGamesCollectionController` | Cache ODS | Supprimer |
| `/collections/videogames/download` | `GET` | `UserGamesCollectionController` | Fichier ODS global | Conserver, mais lire `t_user.collection_file_path` et envoyer le fichier brut |
| `/collections/videogames/games/search` | `GET` | `UserGamesCollectionController` | ODS via `GamesService.search_by_game_name` | Remplacer par lecture SQL utilisateur |
| `/collections/videogames/games` | `POST` | `UserGamesCollectionController` | Écriture ODS | Conserver en `501 Not Implemented` |
| `/collections/videogames/games` | `PUT` | `UserGamesCollectionController` | Écriture ODS | Conserver en `501 Not Implemented` |
| `/collections/videogames/games` | `DELETE` | `UserGamesCollectionController` | Écriture ODS | Conserver en `501 Not Implemented` |
| `/collections/videogames/platforms` | `GET` | `PlatformController` | ODS via `GamesService.list_platforms` | Supprimer |
| `/collections/videogames/platform-image/<platform>` | `GET` | `PlatformController` | Image ODS via `GamesService.get_platform_image` | Supprimer |
| `/collections/videogames/column-values` | `GET` | `PlatformController` | ODS via `GamesService.list_column_values` | Supprimer |
| `/collections/videogames/add-game-choices` | `GET` | `PlatformController` | ODS via `AddGameChoiceService` | Supprimer |
| `/collections/videogames/wishlist/games` | `POST` | `UserWishListController` | Écriture ODS wishlist | Supprimer |
| `/collections/videogames/wishlist/games` | `PUT` | `UserWishListController` | Écriture ODS wishlist | Supprimer |
| `/collections/videogames/wishlist/games` | `DELETE` | `UserWishListController` | Écriture ODS wishlist | Supprimer |
| `/api/library/entities` | `GET` | `PlatformController` | SQL public | Conserver |
| `/api/library/platforms` | `GET` | `PlatformController` | SQL public | Conserver |
| `/api/library/studios` | `GET` | `StudioController` | SQL public | Conserver |
| `/api/library/games` | `GET` | `GameController` | SQL public | Conserver |
| `/api/users/me/collection` | `GET` | `UserCollectionImportController` | SQL utilisateur | Conserver |
| `/api/users/import` | `POST` | `UserCollectionImportController` | Import ODS utilisateur | Conserver |

## Tableau des endpoints cibles

| Endpoint | Méthode | Controller cible | Service cible | Statut |
| --- | --- | --- | --- | --- |
| `/collections/videogames` | `GET` | `CollectionController` | `UserCollectionQueryService` | Créé |
| `/collections/videogames/platforms/search` | `GET` | `CollectionController` | `UserCollectionQueryService` | Créé |
| `/collections/videogames/games/search` | `GET` | `CollectionController` | `UserCollectionQueryService` | Remplacé |
| `/collections/videogames/download` | `GET` | `CollectionController` | `UserCollectionFileService` ou méthode dédiée de consultation | Remplacé |
| `/collections/videogames/games` | `POST` | `CollectionController` | Aucun workflow métier pour l'instant | Conservé en `501` |
| `/collections/videogames/games` | `PUT` | `CollectionController` | Aucun workflow métier pour l'instant | Conservé en `501` |
| `/collections/videogames/games` | `DELETE` | `CollectionController` | Aucun workflow métier pour l'instant | Conservé en `501` |
| `/collections/videogames/home` | `GET` | Aucun | Aucun | Supprimé |
| `/collections/videogames/cache/reset` | `POST` | Aucun | Aucun | Supprimé |
| `/collections/videogames/search` | `GET` | Aucun | Aucun | Supprimé |
| `/collections/videogames/platforms` | `GET` | Aucun | Aucun | Supprimé |
| `/collections/videogames/column-values` | `GET` | Aucun | Aucun | Supprimé |
| `/collections/videogames/add-game-choices` | `GET` | Aucun | Aucun | Supprimé |
| `/collections/videogames/platform-image/<platform>` | `GET` | Aucun | Aucun | Supprimé |
| `/collections/videogames/wishlist/games` | `POST/PUT/DELETE` | Aucun | Aucun | Supprimé |

Les endpoints supprimés doivent être absents de `/api/routes`. Les actions
`POST`, `PUT` et `DELETE /collections/videogames/games` restent dans
`/api/routes` puisqu'elles restent enregistrées en `501`.

## Contrôleurs backend

### `backend/controllers/user_games_collection_controller.py`

État actuel :

- porte les routes principales de consultation collection ;
- dépend de `GamesService` ;
- lit l'ODS pour recherche, accueil, recherche globale et téléchargement ;
- écrit l'ODS pour ajout, modification et suppression de jeu.

Décision :

- renommer en `backend/controllers/collection_controller.py` ;
- renommer la classe en `CollectionController` ;
- remplacer la dépendance `GamesService` par un service SQL de consultation ;
- conserver seulement les routes cibles ;
- transformer `POST`, `PUT`, `DELETE /collections/videogames/games` en réponses
  `501 Not Implemented`.

### `backend/controllers/platform_controller.py`

État actuel :

- mélange routes Bibliothèque publiques SQL et routes de collection ODS ;
- dépend de `GamesService` pour les routes collection ;
- dépend de `LibraryService` pour les routes publiques.

Décision :

- conserver dans ce controller les routes publiques Bibliothèque ;
- supprimer les routes collection ODS ;
- supprimer `games_service_factory` si plus utilisé.

### `backend/controllers/user_wishlist_controller.py`

État actuel :

- porte les écritures wishlist dans l'ODS ;
- dépend de `GamesService`.

Décision :

- supprimer le controller ;
- supprimer son import et son instanciation dans `backend/app.py` ;
- supprimer ses routes de `/api/routes`.

### `backend/app.py`

Modifications prévues :

- remplacer l'import et l'instanciation de `UserGamesCollectionController` par
  `CollectionController` ;
- retirer `UserWishListController` ;
- ne plus injecter `GamesService` dans les controllers de consultation ;
- garder `PlatformController`, `StudioController` et `GameController` pour la
  Bibliothèque.

## Services ODS et décisions

| Fichier | Usage actuel | Décision |
| --- | --- | --- |
| `backend/services/games/games_service.py` | Façade ODS pour consultation, écriture, cache, image, download et wishlist | Supprimer après migration si aucune méthode utile à l'import ne reste |
| `backend/services/games/add_game_choice_service.py` | Fusion de choix depuis feuilles ODS et wishlist | Supprimer avec `/add-game-choices` |
| `backend/services/ods/ods_reader.py` | Lecteur ODS générique utilisé par consultation et import | Conserver seulement si requis par import, sinon déplacer les morceaux utiles |
| `backend/services/ods/ods_collection_import_reader.py` | Lecteur ODS dédié import utilisateur | Conserver comme base du flux import |
| Writer ODS et éditeurs associés | Écriture ODS collection et wishlist | Supprimés après retrait des actions ODS |
| `backend/services/ods/ods_image_reader.py` | Lecture images embarquées ODS | Supprimer du flux consultation ; conserver seulement si import en dépend, ce qui n'est pas le cas actuellement |
| `backend/services/ods/ods_cache.py` | Cache de lecture ODS | Supprimer du flux consultation ; conserver seulement si import garde `OdsReader` |
| `backend/services/ods/ods_path_resolver.py` | Résolution `JEUXVIDEO_ODS_PATH` | Supprimer du flux consultation |

Architecture recommandée :

- ne pas créer `services/collection/ods/UserCollectionODSReader` si
  `OdsCollectionImportReader` couvre déjà le besoin d'import ;
- si une factorisation est nécessaire, déplacer uniquement les fonctions
  strictement utiles à l'import dans un lecteur d'import, pas dans la
  consultation SQL.

## Repositories SQL existants

### Disponibles

- `SqlAlchemyPlatformRepository`
  (`backend/services/database/platform_repository.py`) :
  chargement par clé normalisée, insertion, lectures Bibliothèque publiques.
- `SqlAlchemyStudioRepository`
  (`backend/services/database/studio_repository.py`) :
  chargement par clé normalisée, insertion, lectures Bibliothèque publiques.
- `SqlAlchemyGameRepository`
  (`backend/services/database/game_repository.py`) :
  chargement par couple `(platform, name)`, insertion, lectures Bibliothèque
  publiques.
- `SqlAlchemyUserCollectionRepository`
  (`backend/services/database/user_collection_repository.py`) :
  création d'associations `t_user_collection`.
- `SqlAlchemyUserCollectionFileRepository`
  (`backend/services/database/user_collection_file_repository.py`) :
  vérification et mise à jour de `t_user.collection_file_path`.
- `SqlAlchemyUserCollectionImportRepository`
  (`backend/services/database/user_collection_import_repository.py`) :
  orchestration transactionnelle d'import.

### À étendre ou créer

Créer une couche de lecture dédiée plutôt que surcharger les méthodes d'import :

- soit étendre `SqlAlchemyUserCollectionRepository` avec les lectures de
  consultation ;
- soit créer `SqlAlchemyUserCollectionQueryRepository` pour isoler les requêtes
  paginées de consultation.

Méthodes attendues :

- compter les jeux d'un utilisateur ;
- calculer la plateforme avec le plus de jeux ;
- compter et lister les plateformes d'un utilisateur ;
- compter et lister les jeux d'un utilisateur ;
- lire `collection_file_path` pour le téléchargement.

Les repositories doivent rester sous `backend/services/database/` pour respecter
`documentation/backend-arch.md` et `documentation/database.md`.

## Modèles et champs database

Tables et champs confirmés :

- `t_user.id`
- `t_user.collection_file_path`
- `t_user_collection.user_id`
- `t_user_collection.game_id`
- `t_user_collection.game_additional_name`
- `t_game.id`
- `t_game.name`
- `t_game.release_date`
- `t_game.developer`
- `t_game.platform`
- `t_platform.id`
- `t_platform.name`
- `t_studio.id`
- `t_studio.name`

Jointures cibles :

```sql
t_user_collection.user_id = :user_id
t_user_collection.game_id = t_game.id
t_game.platform = t_platform.id
t_game.developer = t_studio.id
```

`t_game.editor` existe mais n'est pas requis par le contrat actuel.

## Architecture backend cible

### Controller

Créer `backend/controllers/collection_controller.py`.

Responsabilités :

- enregistrer les routes `/collections/videogames/**` conservées ou créées ;
- lire les paramètres HTTP ;
- récupérer l'utilisateur connecté via les mécanismes existants ;
- appeler le service métier ;
- mapper les erreurs en HTTP ;
- retourner `501` pour les actions futures.

Le controller ne doit pas :

- instancier `GamesService` ;
- manipuler SQL directement ;
- parser un fichier ODS.

### Service métier

Créer `backend/services/collection/user_collection_query_service.py` ou un nom
équivalent.

Responsabilités :

- orchestrer les lectures SQL ;
- normaliser les réponses API ;
- retourner les réponses vides attendues ;
- gérer le téléchargement brut via un chemin lu en base, sans parser l'ODS.

Le service peut réutiliser :

- `DatabaseConfiguration` ;
- `create_engine` comme `LibraryService` ;
- `UserCollectionNameNormalizer` ;
- la logique de pagination et payload de page inspirée de `LibraryService`.

### Critères et parsing

Deux options possibles :

1. Étendre `LibraryQueryParser` avec des entités `collection_platforms` et
   `collection_games`.
2. Créer un parseur dédié, par exemple `UserCollectionQueryParser`, pour gérer
   `platform_id`, `platform_name`, `studio_name` et `release_date`.

Recommandation : créer un parseur dédié ou une petite extension ciblée, car le
contrat de recherche de jeux utilisateur dépasse le filtre `name` de la
Bibliothèque.

## Pagination, tri et filtres

À réutiliser :

- page par défaut `0` ;
- taille par défaut `500` ;
- taille maximum `500` ;
- tri invalide remplacé par `name,asc` ;
- payload `page` avec `totalElements`, `page`, `size`, `totalPages`.

À ajouter :

- filtre `name` sans casse et sans accents ;
- filtre `studio_name` sans casse et sans accents ;
- filtre `platform_name` sans casse et sans accents ;
- filtre exact `platform_id` ;
- filtre `release_date=YYYY-MM-DD..YYYY-MM-DD`.

Le helper `LibraryQuerySqlBuilder.build_name_filter` ne suffit pas tel quel
pour combiner plusieurs filtres. Prévoir un builder dédié ou enrichir le helper
pour construire une clause `WHERE` multi-critères.

## Architecture frontend cible

### Services

`frontend/src/services/VideoGamesApi.js` doit remplacer les appels ODS par :

- `fetchCollectionStats()` -> `GET /collections/videogames`
- `fetchPlatforms(criteria)` -> `GET /collections/videogames/platforms/search`
- `fetchGames(criteria)` -> `GET /collections/videogames/games/search`
- `downloadOdsFile()` -> inchangé côté chemin, mais contrat backend modifié

À supprimer :

- `fetchHomeStats()`
- `fetchColumnValues()`
- `searchGamesByName()` si l'accueil n'a plus de recherche globale dédiée, ou
  le rebrancher sur `games/search`
- `resetCache()`
- `fetchProtectedImageObjectUrl()` si plus aucune image ODS n'est affichée
- `deleteWishlistGame()`
- `updateWishlistGame()`

Supprimer aussi :

- `frontend/src/services/AddGameChoicesApi.js`
- `frontend/src/services/WishlistAddApi.js`
- `frontend/src/services/WishlistSortService.js` si uniquement wishlist.

### Hooks

À modifier :

- `useHomePage` : charger les statistiques SQL et ne plus gérer les images ODS.
- `usePlatformsCatalog` : charger les plateformes SQL avec objets `{id, name}`.
- `useGameCollectionPage` : charger les jeux SQL via `platform_id`.
- `useAppNavigation` : remplacer le paramètre URL `platform` par
  `platform_id`.
- `useCloudCollectionViewModel` : retirer la composition wishlist et adapter
  les props.
- `useBackendActionPermissions` et `BackendRouteAccessService` : retirer les
  permissions wishlist et cache reset.
- `useOdsDownload` : conserver, mais gérer le `404` backend.

À supprimer :

- `useWishlistPage`
- `useWishlistGameMutations`
- les usages wishlist dans `useAddGamePage`.

### Composants

À modifier :

- `AppViewSwitch` : retirer le rendu wishlist et adapter les vues collection.
- `MainMenu` : retirer toute entrée wishlist éventuelle.
- `HomeView` : ne plus dépendre de `image_url`, `sheet_name`, `games_count`,
  `total_price`, `average_price` issus de l'ODS.
- `PlatformDetailView` : utiliser `platform_id`, `platform_name`, `nb_games`,
  `total_value`, `average_value`.

À supprimer si plus référencés :

- `WishlistView`
- `WishlistTableActions`
- `EditWishlistDialog`
- composants ou styles strictement wishlist.

## Stratégie de suppression wishlist

Backend :

- supprimer `UserWishListController` ;
- retirer son import, instanciation et `register_routes` dans `backend/app.py` ;
- supprimer les méthodes wishlist de `GamesService` si `GamesService` est
  supprimé ;
- supprimer les tests de routes wishlist ou les remplacer par tests `404`.

Frontend :

- supprimer route `/wishlist` de `AppRouting` ;
- supprimer `AppRouting.wishlistSheetName` ;
- supprimer callbacks `openWishlist` ;
- supprimer services, hooks et composants wishlist ;
- retirer les permissions wishlist ;
- supprimer les entrées menu et boutons liés.

Documentation :

- retirer les endpoints wishlist de `documentation/backend-api.md` ;
- mettre à jour `documentation/site-plan.md` et `documentation/menu.md` si la
  wishlist y est décrite.

## Stratégie de suppression des routes ODS hors import

Supprimer les routes listées dans la tâche principale et vérifier :

- absence dans `/api/routes` ;
- retour `404` par non-enregistrement ;
- absence d'appels frontend ;
- absence d'instanciation `GamesService` dans les controllers de consultation ;
- absence de dépendance à `JEUXVIDEO_ODS_PATH` pour la consultation.

Le seul accès ODS accepté après cette évolution :

- import utilisateur via `POST /api/users/import` ;
- téléchargement brut du fichier importé via
  `GET /collections/videogames/download`.

## Tests backend à ajouter ou modifier

Tests de service/repository :

- statistiques globales pour un utilisateur avec collection ;
- statistiques globales vides pour un utilisateur sans collection ;
- plateforme `max_platform` calculée correctement ;
- plateformes filtrées par utilisateur connecté ;
- jeux filtrés par utilisateur connecté ;
- isolation entre deux utilisateurs ;
- recherche sans casse et sans accents ;
- pagination ;
- tri autorisé et fallback sur tri invalide ;
- filtre `platform_id` ;
- filtre `release_date=YYYY-MM-DD..YYYY-MM-DD`.

Tests de routes :

- `GET /collections/videogames` ;
- `GET /collections/videogames/platforms/search` ;
- `GET /collections/videogames/games/search` ;
- `GET /collections/videogames/download` avec fichier existant ;
- `GET /collections/videogames/download` avec `collection_file_path` vide ;
- `GET /collections/videogames/download` avec fichier absent ;
- `POST`, `PUT`, `DELETE /collections/videogames/games` en `501` ;
- anciens endpoints ODS en `404` ;
- endpoints supprimés absents de `/api/routes` ;
- endpoints wishlist en `404`.

Tests existants à mettre à jour :

- `backend/tests/test_collection_routes.py`
- `backend/tests/test_game_mutation_routes.py`
- `backend/tests/test_ods_reader.py` si des lecteurs ODS sont supprimés ou
  recentrés import
- `backend/tests/route_test_fakes.py`
- tests de routing `/api/routes` si présents.

## Validations frontend à effectuer

- `npm run build` ;
- vérifier que la page `Ma collection` affiche les stats et plateformes SQL ;
- vérifier que la page plateforme charge les jeux via `platform_id` ;
- vérifier le cas sans collection ;
- vérifier que la wishlist n'est plus navigable ;
- vérifier que le téléchargement ODS gère le `404`.

## Documentation à mettre à jour

- `README.md` : nouvelle consultation SQL, suppression wishlist et routes ODS.
- `documentation/backend-api.md` : endpoints cibles, endpoints supprimés,
  actions `501`, download utilisateur.
- `documentation/backend-arch.md` : `CollectionController` et service SQL de
  consultation.
- `documentation/frontend-arch.md` : hooks et services frontend après retrait
  ODS/wishlist.
- `documentation/database.md` : préciser la consultation via
  `t_user_collection` si nécessaire.
- `documentation/site-plan.md` : suppression wishlist et navigation par
  `platform_id`.
- `documentation/menu.md` : suppression entrée wishlist si documentée.
- `documentation/about.md` : vérifier les mentions de l'image issue de l'ODS
  `Accueil`, qui devient obsolète si l'affichage n'utilise plus cette image.
- `documentation/ci.md` : vérifier les mentions de `JEUXVIDEO_ODS_PATH` pour les
  tests backend.

## Risques et points à valider

- `LibraryQueryParser` ne supporte pas les filtres `studio_name`,
  `platform_name`, `platform_id` et plage `release_date`. Prévoir un parseur
  dédié ou une extension propre.
- Les colonnes `buy_date` et `grade` n'existent pas encore en base. Le tri sur
  ces colonnes doit retourner un fallback stable ou utiliser des expressions
  constantes tant que les champs retournent `""`.
- Les actions `POST`, `PUT`, `DELETE /collections/videogames/games` restent
  dans `/api/routes`. Le frontend doit éviter de réafficher des actions actives
  uniquement parce que le catalogue les annonce.
- La suppression de `GamesService` peut impacter de nombreux tests existants.
  Mieux vaut supprimer les routes ODS avant de supprimer les classes bas niveau,
  puis vérifier les usages restants.
- Le composant `HomeView` dépend aujourd'hui de `platform.image_url`,
  `sheet_name`, `games_count`, `total_price`, `average_price`. Le contrat SQL
  cible utilise `id`, `name`, `nb_games`, `total_value`, `average_value`.
  Adapter explicitement le mapping.
- La route URL actuelle utilise `?platform=<nom>`. La cible demande
  `platform_id`. Il faut adapter `AppRouting`, `useAppNavigation`,
  `usePlatformsCatalog` et les liens depuis les cartes.
- Les routes publiques Bibliothèque dans `PlatformController` doivent être
  préservées lors de l'extraction des routes collection.

## Ordre d'implémentation recommandé

1. Finaliser le contrat et corriger les libellés de tâche.
2. Créer le service/repository SQL de consultation avec tests.
3. Créer `CollectionController` et brancher les routes cibles.
4. Supprimer les anciennes routes ODS.
5. Supprimer la wishlist.
6. Adapter le frontend.
7. Nettoyer les services ODS, mettre à jour la documentation et valider.
