# 00 - Rapport d'analyse du code existant

## Synthese

Le workflow actuel d'import utilisateur est deja generique sur le type de
fichier et sur la description des feuilles : le frontend depose un fichier,
demande son analyse, construit une configuration JSON, puis le backend valide
cette configuration et lit le fichier via `CollectionFileReaderFactory`.

L'information `wishlist` n'existe pas encore dans le schema SQL, les DTOs
d'import, les readers, la persistance ou les endpoints de consultation. La
future implementation doit donc etendre le contrat de configuration, transporter
un booleen par jeu importe, persister ce booleen dans `t_user_collection`, puis
filtrer les lectures SQL de collection sur `wishlist=false`.

La tache chapeau contredit volontairement deux documents actuels :

- `documentation/import.md` et `documentation/site-plan.md` demandent encore
  une redirection automatique vers `/collection` apres import reussi ;
- `tasks/0.2.0/import_wishlist/import_wishlist.md` demande de remplacer cette
  redirection par un ecran de resume avec lien vers la collection.

Cette divergence doit etre traitee comme une evolution de contrat a documenter
en tache `07`, pas comme une modification documentaire dans cette tache `00`.

## Documentations Relues

- `documentation/import.md` : workflow import, regles de persistance atomique,
  routes `POST /api/users/import/*`, redirection actuelle post-import.
- `documentation/backend-api.md` : contrats actuels de
  `POST /api/users/import`, `GET /collections/videogames` et
  `GET /collections/videogames/games/search`.
- `documentation/backend-arch.md` : controllers HTTP sous
  `backend/controllers/`, services metier sous `backend/services/`, readers ODS
  sous `backend/services/ods/`, repositories SQL sous
  `backend/services/database/`.
- `documentation/frontend-arch.md` : orchestration React dans
  `frontend/src/hooks/collection/`, appels HTTP dans `frontend/src/services/`,
  composants dedies au rendu.
- `documentation/database.md` : schema courant sans colonne
  `t_user_collection.wishlist`; toute modification doit passer par Alembic et
  mettre a jour le contrat de schema.
- `documentation/site-plan.md` : routes `/collection` et `/collection/import`,
  restrictions non-`ADMIN`, redirection actuelle post-import.
- `tasks/0.2.0/import_wishlist/import_wishlist.md` : contrat cible wishlist,
  modes `none`, `sheet`, `column`, compteurs et documentation attendue.

## Cartographie Backend Actuelle

### Controller d'import

`backend/controllers/user_collection_import_controller.py`

- Enregistre :
  - `GET /api/users/me/collection`
  - `POST /api/users/import/file/<file_type>`
  - `POST /api/users/import/analyze/<file_type>`
  - `POST /api/users/import`
- Derive toujours l'utilisateur depuis le Bearer token.
- Sauvegarde l'upload dans un fichier temporaire local, puis delegue a
  `UserCollectionImportService.upload_import_file`.
- Parse le JSON final avec `_parse_collection_file_description_json`.
- Valide le payload avec `CollectionFileDescriptionValidator`.
- Mappe deja les erreurs de configuration en `422`, les fichiers invalides en
  `400`, les fichiers temporaires absents en `404`, les conflits en `409` et les
  fichiers trop gros en `413`.

Impact cible : conserver le controller comme couche HTTP. Il doit seulement
recevoir le nouveau contrat `wishlist` via le validateur existant et retourner
les nouveaux compteurs du service.

### Service d'import utilisateur

`backend/services/users/user_collection_import_service.py`

- Orchestre l'import complet et applique un verrou applicatif par utilisateur.
- Verifie l'absence de collection preexistante.
- Valide l'extension via `reader.accepted_extensions`.
- Copie le fichier dans `/users/workspace/<user_id>/<user_id>-collection.ods`.
- Appelle `reader.read(str(copied_file_path), file_description)`.
- Appelle `repository.import_collection(user_id, path, import_data, description)`.
- Retourne `UserCollectionImportResult`.

Impact cible :

- ajouter `wishlisted_games` et `warnings` a `UserCollectionImportResult` ;
- mapper les warnings produits par le reader ou le modele d'import ;
- laisser les decisions de lecture wishlist au reader et les decisions de
  persistance au repository.

### Contrat de configuration d'import

`backend/services/collection/imports/collection_file_description.py`

- `CollectionImportField` contient actuellement `name`, `platform`, `studio`,
  `release_date`.
- `CollectionSheetLayout` porte `data_range`, `header_row`,
  `column_information`, `included_sheets`, `excluded_sheets`.
- `CollectionFileDescription` porte `file_type`, `single_sheet_conf`,
  `multiple_sheets_conf`.

`backend/services/collection/imports/collection_file_description_validator.py`

- Valide `file_type`.
- Valide l'exclusivite `single_sheet_conf` / `multiple_sheets_conf`.
- Valide les layouts, les colonnes et les feuilles incluses/exclues.
- Refuse tout champ inconnu dans `column_information`.

Impact cible :

- creer `WishlistImportMode` avec `NONE = "none"`, `SHEET = "sheet"`,
  `COLUMN = "column"` ;
- creer `WishlistImportConfiguration` pour le top-level `wishlist` ;
- ajouter `CollectionImportField.WISHLIST = "wishlist"` ;
- ajouter `wishlist: WishlistImportConfiguration` dans
  `CollectionFileDescription` ;
- rendre `wishlist` obligatoire dans le payload final ;
- valider les incoherences propres aux modes wishlist.

### DTOs de donnees importees

`backend/services/collection/imports/collection_import_models.py`

- `CollectionImportPlatform`
- `CollectionImportStudio`
- `CollectionImportGame`
- `CollectionImportData`

`CollectionImportGame` porte actuellement `name`, `platform_name`,
`studio_name`, `release_date`.

Impact cible :

- ajouter `wishlist: bool = False` a `CollectionImportGame` ;
- ajouter un modele de warnings, par exemple
  `CollectionImportWarnings(invalid_wishlist: int, invalid_wishlist_values_found: list[str])` ;
- ajouter `warnings: CollectionImportWarnings` dans `CollectionImportData` ou
  retourner un objet d'import plus riche ;
- eviter de stocker des warnings dans le service si le reader peut les produire
  au moment du parsing.

### Factory et readers

`backend/services/collection/imports/collection_file_reader_factory.py`

- Cree le reader pour `CollectionFileType.LIBREOFFICE_ODS`.

`backend/services/ods/ods_collection_import_reader.py`

- Liste les onglets avec `OdsReader.list_sheets()`.
- Lit un layout single-sheet ou multi-sheet.
- Dedoublonne sur `(platform_name, game_key)` avec conservation du premier.
- Ignore les lignes sans nom de jeu.
- Journalise les doublons.
- Construit les plateformes et studios a partir des jeux retenus.

Impact cible :

- lire `description.wishlist.mode` dans `_read_configured_games` ;
- mode `none` : garder le comportement actuel avec `wishlist=false` ;
- mode `sheet` : lire l'onglet dedie via un `CollectionSheetLayout` specifique
  et forcer `wishlist=true` pour ses lignes ;
- mode `column` : lire la colonne `wishlist` de chaque layout collection,
  parser la valeur, ignorer la ligne si la valeur est invalide et alimenter les
  warnings ;
- extraire le parsing booleen dans une classe dediee,
  `WishlistValueParser`, sous `backend/services/collection/imports/`.

### Persistance SQL

`backend/services/database/user_collection.py`

- ORM `UserCollection` avec `user_id`, `game_id`, `game_additional_name`.

`backend/services/database/user_collection_repository.py`

- `ensure_user_game_associations(connection, user_id, game_ids)` insere les
  associations manquantes sans information additionnelle.

`backend/services/database/user_collection_import_repository.py`

- Coordonne la transaction d'import.
- Cree/reutilise plateformes, studios et jeux.
- Appelle `ensure_user_game_associations`.
- Met a jour `t_user.collection_file_path` et
  `t_user.collection_file_description`.

Impact cible :

- ajouter `wishlist` au modele ORM et au schema ;
- remplacer la liste simple `game_ids` par des associations porteuses du booleen
  wishlist, par exemple `CollectionImportGameAssociation(game_id, wishlist)` ou
  un dictionnaire `game_id -> wishlist` ;
- inserer `wishlist` dans `t_user_collection` ;
- conserver les associations existantes sans duplication ;
- decider explicitement si une association existante doit etre mise a jour si
  une nouvelle importation etait permise plus tard. Le workflow actuel interdit
  le second import, donc ce cas reste hors portee immediate.

### Consultation SQL de collection

`backend/controllers/collection_controller.py`

- Enregistre :
  - `GET /collections/videogames`
  - `GET /collections/videogames/platforms/search`
  - `GET /collections/videogames/games/search`
  - `GET /collections/videogames/download`
  - actions `POST/PUT/DELETE /collections/videogames/games` reservees en `501`.

`backend/services/collection/user_collection_query_contract.py`

- Parse pagination, recherche, tri, `platform_id` et plage `release_date`.
- `UserCollectionGameQueryCriteria` ne porte pas encore de filtre `wishlist`.

`backend/services/collection/user_collection_query_service.py`

- `get_statistics` retourne un objet plat : `total`, `total_value`,
  `average_value`, `max_platform`.
- `list_games` retourne les jeux sans champ `wishlist`.

`backend/services/database/user_collection_query_repository.py`

- Toutes les requetes filtrent par `user_collection.user_id`.
- Les statistiques comptent toutes les lignes `t_user_collection`.
- Les recherches jeux ne filtrent pas `wishlist`.

Impact cible :

- ajouter `wishlist: bool | None` dans `UserCollectionGameQueryCriteria` ;
- parser `wishlist=true|false` dans `UserCollectionQueryParser.parse_games` ;
- filtrer `user_collection.wishlist = :wishlist` dans les requetes jeux si le
  parametre est present ;
- retourner `user_collection.wishlist AS wishlist` dans `list_games` ;
- calculer des statistiques separees `collection` et `wishlist` ;
- pour les totaux collection, filtrer `wishlist=false`.

## Cartographie Frontend Actuelle

### Page onboarding

`frontend/src/components/UserCollectionOnboardingView.jsx`

- Affiche toujours les champs de configuration sous l'input fichier.
- Affiche trois etapes dont la troisieme indique que la collection s'ouvre
  automatiquement apres succes.
- Soumet via `onSubmitImport`.

Impact cible :

- masquer la configuration tant que l'analyse backend n'a pas reussi ;
- modifier le texte et le flux post-import pour afficher un resume ;
- ajouter une section wishlist avant les plages collection ;
- afficher un lien/action vers `/collection` au lieu de rediriger
  automatiquement.

### Hook onboarding

`frontend/src/hooks/collection/useUserCollectionOnboarding.js`

- Stocke `selectedCollectionFile`, `availableImportSheets`,
  `importConfiguration`.
- `selectCollectionFile` upload puis analyse le fichier.
- `applyAnalyzedSheets` preconfigure le mode single/multiple sheets.
- `importSelectedCollection` construit le JSON et appelle
  `UserCollectionApi.importCollection(description)`.
- Apres succes, il appelle `reloadOds()`, `reloadGames()` et `goHome()`.

Impact cible :

- ajouter un etat `importResult` et un mode d'affichage resume ;
- supprimer l'appel `goHome()` automatique apres import reussi ;
- exposer des callbacks wishlist (`onWishlistModeChange`,
  `onWishlistLayoutChange`, etc.) ou integrer ces modifications dans les
  callbacks existants ;
- pre-remplir `headerRow` avec la premiere ligne de `dataRange` lorsque la
  plage change ;
- pre-remplir les mappings depuis les colonnes de la plage.

### Builder de configuration

`frontend/src/hooks/collection/importConfigurationBuilder.js`

- `REQUIRED_FIELDS = ["name", "platform", "studio", "release_date"]`.
- `createDefaultImportConfiguration` ne contient aucune section wishlist.
- `buildImportConfigurationDescription` construit `single_sheet_conf` ou
  `multiple_sheets_conf`.
- `buildLayout` construit `column_information`.

Impact cible :

- ajouter `wishlist` a l'etat frontend par defaut avec `mode: "none"` ;
- ajouter `wishlist` au JSON final ;
- en mode `column`, ajouter le champ `wishlist` aux `column_information`
  concernes ;
- en mode `sheet`, construire un layout wishlist dedie ;
- extraire ou reutiliser `LayoutFields` pour eviter de dupliquer les champs de
  mapping.

### Composants de configuration

`frontend/src/components/ImportConfigurationFields.jsx`

- Affiche type de fichier, mode multi-onglets, selection d'onglets, layouts et
  layouts par feuille.
- `LayoutFields` et `PerSheetFields` sont deja reutilisables dans le fichier.

Impact cible :

- extraire `LayoutFields` si necessaire dans un composant reutilisable public,
  par exemple `ImportLayoutFields.jsx`, pour servir collection et onglet
  wishlist ;
- ajouter `WishlistImportConfigurationFields.jsx` ou une section locale dediee ;
- garder la logique metier de validation definitive cote backend.

### Services frontend

`frontend/src/services/UserCollectionApi.js`

- Appelle les routes d'upload, analyse et import.
- Normalise les erreurs par statut.

`frontend/src/services/VideoGamesApi.js`

- Appelle `/collections/videogames`, `/platforms/search` et `/games/search`.
- `fetchGames(platformId)` appelle les jeux par plateforme sans `wishlist`.
- `searchGamesByName(query)` appelle les jeux sans `wishlist`.
- Normalise les jeux sans conserver `wishlist`.

Impact cible :

- faire passer `wishlist=false` aux appels de collection existants ;
- conserver le champ `wishlist` dans la normalisation interne si utile, mais ne
  pas l'afficher dans les colonnes visibles ;
- adapter `fetchHomeStats` au nouveau payload de statistiques `{collection,
  wishlist}`.

## Architecture Cible Proposee

### Contrat JSON wishlist

Contrat a stabiliser en tache `01` :

```json
{
  "file_type": "libreoffice_ods",
  "wishlist": {
    "mode": "none"
  }
}
```

```json
{
  "file_type": "libreoffice_ods",
  "wishlist": {
    "mode": "sheet",
    "sheet_name": "Wishlist",
    "data_range": "A1:H200",
    "header_row": 1,
    "column_information": {
      "name": "A",
      "platform": "B",
      "studio": "C",
      "release_date": "D"
    }
  }
}
```

```json
{
  "file_type": "libreoffice_ods",
  "wishlist": {
    "mode": "column"
  },
  "single_sheet_conf": {
    "data_range": "A1:H200",
    "header_row": 1,
    "column_information": {
      "name": "A",
      "platform": "B",
      "studio": "C",
      "release_date": "D",
      "wishlist": "E"
    }
  }
}
```

Regles proposees :

- `wishlist` obligatoire dans le payload final ;
- `mode=none` interdit `sheet_name`, `data_range`, `header_row` et
  `column_information` dans la section wishlist ;
- `mode=sheet` exige `sheet_name`, `data_range`, `header_row` et
  `column_information` sans champ `wishlist` ;
- `mode=column` exige un mapping `wishlist` dans chaque layout collection
  importe ;
- `mode=column` interdit un layout dedie dans la section wishlist.

### Validation backend

Fichiers a modifier :

- `backend/services/collection/imports/collection_file_description.py`
- `backend/services/collection/imports/collection_file_description_validator.py`
- `backend/services/collection/imports/__init__.py`

Classes et methodes a ajouter ou modifier :

- `CollectionImportField.WISHLIST`
- `WishlistImportMode`
- `WishlistImportConfiguration`
- `CollectionFileDescription.wishlist`
- `CollectionFileDescription.to_dict`
- `CollectionFileDescriptionValidator.validate`
- `CollectionFileDescriptionValidator._build_wishlist_configuration`
- `CollectionFileDescriptionValidator._validate_wishlist_mode_constraints`

### Parsing des valeurs wishlist

Nouveau fichier propose :

`backend/services/collection/imports/wishlist_value_parser.py`

Classe proposee :

- `WishlistValueParser`
  - `parse(value: Any) -> bool | None`
  - `is_invalid(value: Any) -> bool`

Regles proposees :

- valeurs `true` : `oui`, `o`, `true`, `yes`, `y` ;
- valeurs `false` : `non`, `n`, `false`, `no` ;
- casse ignoree et espaces trimmes ;
- valeur vide : `False` ;
- valeur non reconnue : ligne ignoree, warning incremente.

### Lecture ODS

Fichier a modifier :

- `backend/services/ods/ods_collection_import_reader.py`

Methodes impactees :

- `read`
- `_read_configured_games`
- `_read_multiple_sheets_games`
- `_read_layout_games`
- `_build_games`
- `_configured_columns`
- `_column_positions`

Methodes a ajouter :

- `_read_wishlist_sheet_games`
- `_read_collection_layout_games`
- `_parse_wishlist_value`
- `_merge_collection_and_wishlist_games`
- `_deduplicate_game`

Priorite de doublons proposee :

- si un meme jeu est lu en collection reelle et dans l'onglet wishlist,
  conserver `wishlist=false` ;
- si un meme jeu est duplique dans l'onglet wishlist, conserver le premier ;
- si un doublon `wishlist=true` / `wishlist=false` existe dans le mode colonne,
  appliquer la regle de la tache chapeau : conserver le premier `wishlist=true`.

Cette derniere regle est en tension avec la regle precedente collection vs
onglet dedie. Le rapport propose de fermer la decision ainsi :

- `sheet` : la collection reelle gagne sur l'onglet wishlist ;
- `column` : le premier `wishlist=true` gagne sur un doublon `wishlist=false`.

### Persistance SQL

Fichiers a modifier :

- `backend/services/database/user_collection.py`
- `backend/services/database/user_collection_repository.py`
- `backend/services/database/user_collection_import_repository.py`
- `backend/services/database/__init__.py` si les exports changent
- `backend/migrations/versions/<nouvelle_revision>_add_user_collection_wishlist.py`

Migration proposee :

- `ALTER TABLE <schema>.t_user_collection ADD COLUMN IF NOT EXISTS wishlist BOOLEAN NOT NULL DEFAULT false`
- ajouter un index utile si les requetes filtrent souvent par utilisateur et
  wishlist, par exemple `ix_t_user_collection_user_wishlist(user_id, wishlist)`.

Methodes impactees :

- `SqlAlchemyUserCollectionRepository.ensure_user_game_associations`
- `SqlAlchemyUserCollectionImportRepository.import_collection`
- `SqlAlchemyUserCollectionImportRepository._ensure_games`

Nouveau modele interne possible :

- `UserGameAssociationImport(game_id: int, wishlist: bool)`

### Consultation backend

Fichiers a modifier :

- `backend/services/collection/user_collection_query_contract.py`
- `backend/services/collection/user_collection_query_service.py`
- `backend/services/database/user_collection_query_repository.py`
- `backend/controllers/collection_controller.py` uniquement si un mapping HTTP
  supplementaire est necessaire.

Methodes impactees :

- `UserCollectionQueryParser.parse_games`
- `SqlAlchemyUserCollectionQueryRepository.count_collection_games`
- `SqlAlchemyUserCollectionQueryRepository.find_max_platform_name`
- `SqlAlchemyUserCollectionQueryRepository.count_games_by_criteria`
- `SqlAlchemyUserCollectionQueryRepository.list_games`
- `UserCollectionQueryService.get_statistics`
- `UserCollectionQueryService._game_payload`

Contrat cible propose pour `GET /collections/videogames` :

```json
{
  "collection": {
    "total": 420,
    "total_value": 0,
    "average_value": 0,
    "max_platform": "Switch"
  },
  "wishlist": {
    "total": 12,
    "total_value": 0,
    "average_value": 0,
    "max_platform": "PS5"
  }
}
```

Contrat cible propose pour `GET /collections/videogames/games/search` :

- accepter `wishlist=true` ou `wishlist=false` ;
- sans parametre, conserver toutes les lignes ou choisir explicitement
  `wishlist=false` cote frontend. Pour limiter les surprises API, le rapport
  recommande que le backend accepte l'absence de filtre comme "toutes les
  lignes" et que la page collection envoie toujours `wishlist=false`.

### Frontend onboarding

Fichiers a modifier :

- `frontend/src/hooks/collection/importConfigurationBuilder.js`
- `frontend/src/hooks/collection/useUserCollectionOnboarding.js`
- `frontend/src/components/UserCollectionOnboardingView.jsx`
- `frontend/src/components/ImportConfigurationFields.jsx`
- `frontend/src/styles/collection-onboarding.css`

Fichiers possibles a creer :

- `frontend/src/components/WishlistImportConfigurationFields.jsx`
- `frontend/src/components/ImportLayoutFields.jsx` si extraction de
  `LayoutFields` necessaire
- `frontend/src/components/UserCollectionImportSummaryView.jsx` ou rendu resume
  local dans `UserCollectionOnboardingView.jsx` si le fichier reste sous 500
  lignes.

Etat frontend cible :

- `importConfiguration.wishlist.mode`
- `importConfiguration.wishlist.sheetName`
- `importConfiguration.wishlist.layout`
- `importResult`
- `showImportConfiguration` derive de `availableImportSheets.length` ou d'un
  flag d'analyse reussie.

### Frontend consultation collection

Fichiers a modifier :

- `frontend/src/services/VideoGamesApi.js`
- `frontend/src/hooks/games/useGameCollectionPage.js` si l'API devient plus
  parametrable
- `frontend/src/hooks/home/useHomePage.js` seulement si le mapping home n'est
  pas entierement dans `VideoGamesApi.fetchHomeStats`

Regles cible :

- `fetchGames(platformId)` appelle
  `/collections/videogames/games/search?platform_id=<id>&wishlist=false` ;
- `searchGamesByName(query)` appelle
  `/collections/videogames/games/search?name=<query>&wishlist=false` ;
- `fetchHomeStats` lit `statistics.collection` et ignore `statistics.wishlist`
  pour les compteurs existants ;
- le champ `wishlist` retourne par l'API ne devient pas une colonne visible.

## Tests A Modifier Ou Ajouter

### Backend

- `backend/tests/test_collection_file_description_validator.py`
  - modes `none`, `sheet`, `column` valides ;
  - `wishlist` absent -> `422` ;
  - mode inconnu -> `422` ;
  - mode `sheet` sans layout -> `422` ;
  - mode `column` sans colonne `wishlist` -> `422`.
- `backend/tests/test_configurable_ods_collection_import_reader.py`
  - mode `none` ;
  - mode `sheet` ;
  - mode `column` avec valeurs valides ;
  - valeur wishlist vide -> `False` ;
  - valeur invalide -> ligne ignoree et warning ;
  - doublons selon les priorites decidees.
- `backend/tests/test_user_collection_import_service.py`
  - retour `wishlisted_games` ;
  - warnings serialises ;
  - description sauvegardee avec section `wishlist`.
- `backend/tests/test_user_collection_import_service_generic_reader.py`
  - reader generique transmet bien les informations wishlist.
- `backend/tests/test_user_collection_import_repository.py` a creer ou completer
  si absent :
  - insertion `wishlist=false` par defaut ;
  - insertion `wishlist=true` ;
  - compteurs d'association.
- `backend/tests/test_database_schema_service.py`
  - schema/migration contient la colonne `wishlist`.
- `backend/tests/test_user_collection_query_repository.py`
  - filtres SQL `wishlist=true` et `wishlist=false` ;
  - champ `wishlist` retourne ;
  - statistiques separees.
- `backend/tests/test_user_collection_query_service.py`
  - payload `{collection, wishlist}` ;
  - mapping `wishlist` des jeux.
- `backend/tests/test_collection_routes.py`
  - contrats HTTP des nouvelles statistiques et du filtre.
- `backend/tests/test_user_collection_routes.py`
  - `POST /api/users/import` retourne les nouveaux compteurs.

### Frontend

Il n'y a pas de suite de tests frontend visible dans le depot. Validation cible
minimale :

- `cd frontend && npm run build` ;
- verification manuelle du workflow import :
  - configuration cachee avant analyse ;
  - mode sans wishlist ;
  - mode onglet dedie ;
  - mode colonne ;
  - resume post-import ;
  - lien vers collection ;
  - page collection sans entrees wishlist.

Si une suite frontend est ajoutee plus tard, cibler :

- `importConfigurationBuilder` pour les trois contrats JSON ;
- `useUserCollectionOnboarding` pour l'absence de redirection automatique ;
- `VideoGamesApi` pour `wishlist=false`.

## Risques Identifies

- Les regles de priorite des doublons contiennent une tension entre le mode
  onglet dedie et le mode colonne. La tache `01` doit fermer cette decision.
- Ajouter `wishlist` a `CollectionImportField` peut rendre le champ acceptable
  partout ; le validateur doit le rendre obligatoire uniquement en mode
  `column`.
- Les statistiques actuelles sont un objet plat. Le passage a
  `{collection, wishlist}` est une rupture de contrat frontend et documentaire.
- La documentation actuelle impose une redirection post-import ; la nouvelle
  specification demande un ecran de resume. Cela doit etre documente et annonce
  explicitement.
- Les requetes plateformes ne mentionnent pas de filtre wishlist. Si les
  plateformes de la page collection doivent exclure les souhaits, les endpoints
  plateformes doivent aussi filtrer `wishlist=false`, meme si la tache chapeau
  insiste surtout sur la recherche jeux.
- La colonne `wishlist BOOLEAN NOT NULL DEFAULT false` est simple, mais doit
  etre ajoutee par une nouvelle migration, sans modifier une migration deja
  publiee.
- Les warnings d'import doivent rester serialisables et testables sans melanger
  logs techniques et contrat API.

## Decisions De Contrat A Reprendre

- La section top-level `wishlist` est obligatoire dans le JSON final.
- `wishlist.mode` accepte seulement `none`, `sheet`, `column`.
- Valeur SQL par defaut : `false`.
- Valeur wishlist vide en mode colonne : `false`.
- Valeur wishlist invalide : ligne ignoree, import non rollback, warning
  journalise et retourne dans le JSON.
- Mode `sheet` : les lignes de l'onglet dedie sont importees avec
  `wishlist=true`.
- La page collection existante demande explicitement `wishlist=false`.
- Le champ `wishlist` peut etre retourne par le backend mais ne doit pas etre
  affiche comme colonne dans la page collection actuelle.
- Apres import reussi, le frontend affiche un resume et un lien vers la
  collection au lieu de rediriger automatiquement.

## Documents A Mettre A Jour En Fin De Chantier

- `documentation/import.md` : modes wishlist, nouveau resume post-import,
  warnings, absence de redirection automatique.
- `documentation/backend-api.md` : nouveaux contrats de
  `POST /api/users/import`, `GET /collections/videogames` et
  `GET /collections/videogames/games/search`.
- `documentation/database.md` : colonne `t_user_collection.wishlist`, migration
  et index eventuel.
- `documentation/site-plan.md` : comportement post-import et page collection.
- `documentation/collection.md` : a creer pour decrire la consultation de la
  collection utilisateur.
- `README.md` : resume court des impacts utilisateur/maintenance.

## Ecarts Avec La Tache Chapeau

- La tache chapeau demande de creer `documentation/collection.md`, mais
  `AGENTS.md` demande d'attendre confirmation avant de creer un nouveau bloc
  fonctionnel documentaire. Cette creation doit donc etre proposee en tache
  `07` avant application.
- La tache chapeau demande de ne plus rediriger apres import, alors que les
  documentations actuelles demandent encore la redirection. Cette evolution
  change un comportement attendu documente et doit etre confirmee en tache `05`
  ou `07` avant modification documentaire.
- Le filtre wishlist est explicitement demande pour
  `/collections/videogames/games/search`; il faudra verifier si
  `/collections/videogames/platforms/search` doit aussi exclure les souhaits
  pour eviter des plateformes visibles sans jeux reels dans la page collection.

## Criteres D'Acceptation De La Tache 00

- Le rapport existe dans
  `tasks/0.2.0/import_wishlist/00_existing_code_analysis_result.md`.
- Le rapport respecte la separation backend controller/service/repository/ODS
  de `documentation/backend-arch.md`.
- Le rapport respecte la separation frontend hook/service/composant de
  `documentation/frontend-arch.md`.
- Les taches `01` a `07` disposent des fichiers, classes, methodes et tests a
  modifier ou creer sans nouvelle exploration generale.
