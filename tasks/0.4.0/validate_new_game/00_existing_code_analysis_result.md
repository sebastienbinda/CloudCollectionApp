# 00 - Resultat d'analyse du code existant et architecture cible

Date d'analyse : 2026-07-29

## Synthese

La fonctionnalite doit ajouter un statut de validation sur les jeux globaux de
la Bibliotheque sans bloquer l'import utilisateur ni la consultation de sa
propre collection. Le point central du backend est
`SqlAlchemyGameRepository.insert`, appele par l'import utilisateur, l'import CSV
admin et le reset Bibliotheque via le coeur d'import factorise.

Le changement cible doit donc rendre explicite le statut initial selon le
contexte d'import :

- import utilisateur connecte : `WAITING_VALIDATION` pour les nouveaux jeux ;
- import CSV admin : `ACCEPTED` pour les nouveaux jeux ;
- reset Bibliotheque : `ACCEPTED` pour les nouveaux jeux recrees ;
- migration des jeux existants : `ACCEPTED`.

La consultation publique Bibliotheque doit ensuite filtrer les jeux
`ACCEPTED`, sauf pour `ADMIN`, et le detail `/api/library/games/<game_id>` doit
autoriser l'acces d'un `USER` proprietaire quand le jeu est encore
`WAITING_VALIDATION`.

## Cartographie Backend

### Routes Bibliotheque Jeux

- `backend/controllers/game_controller.py`
  - `GET /api/library/games`, endpoint public `list_library_games`.
  - `GET /api/library/games/<game_id>`, endpoint public `get_library_game`.
  - `POST /api/library/games/<game_id>/doublon`, endpoint protege `USER`.
  - `list_library_games` resout deja un Bearer `USER` optionnel via
    `_optional_current_user_id` pour enrichir les marqueurs de collection et de
    wishlist.
  - `get_library_game` ne resout pas encore de Bearer optionnel et appelle
    `LibraryService.get_game(game_id)` sans contexte utilisateur.

### Services, Repositories Et Serialization `t_game`

- `backend/services/library/library_service.py`
  - `count_entities` compte actuellement tous les jeux via
    `count_public_library_games`.
  - `list_games` appelle `count_public_library_games_by_criteria`,
    `list_public_library_games` puis `CurrentUserCollectionMarker.mark_games`.
  - `get_game` appelle `find_public_library_game` sans profil ni utilisateur.
- `backend/services/database/game_repository.py`
  - `insert` insere `name`, `release_date`, `developer`, `editor`,
    `platform`, `description`, `duplicate_flag`; il ne connait pas encore
    `status`.
  - `count_public_library_games`, `count_public_library_games_by_criteria`,
    `list_public_library_games` et `find_public_library_game` ne filtrent pas
    encore par statut.
  - `_build_library_games_where_clause` gere deja `name`, `platform` et
    `duplicate_flag`.
  - `load_references_by_key` et `load_ids_by_key` chargent tous les jeux et
    alias pour le matching d'import, ce qui correspond au besoin : un jeu
    importe peut etre rattache a un jeu de n'importe quel statut.
- `backend/services/database/game.py`
  - Le modele ORM `Game` ne contient pas encore `status`.
- `backend/services/library/library_payload_serializer.py`
  - `game_payload` expose deja une cle `status`, mais les requetes SQL ne
    selectionnent pas encore `game.status`; la valeur actuelle est donc vide.

### Chemins De Creation Des Jeux

- Import utilisateur :
  - `UserCollectionImportService.import_collection`.
  - `SqlAlchemyUserCollectionImportRepository.import_collection`.
  - `_ensure_games`, puis `SqlAlchemyGameRepository.insert` si aucun jeu
    existant/matche n'est trouve.
  - Les associations utilisateur sont creees ensuite par
    `SqlAlchemyUserCollectionRepository.ensure_user_game_associations`.
- Import CSV admin :
  - `LibraryController.import_library_csv`.
  - `AdminLibraryImportService.import_csv_file`.
  - `SqlAlchemyAdminLibraryImportRepository.import_library`.
  - Herite du coeur `_ensure_games` de
    `SqlAlchemyUserCollectionImportRepository`.
- Reset Bibliotheque :
  - `LibraryController.reset_library`.
  - `LibraryResetJobCoordinator.start_reset`.
  - `LibraryResetService.run_reset`.
  - `SqlAlchemyLibraryResetRepository.clean_library_tables`.
  - `StoredUserCollectionImportService.import_stored_collection`, via le meme
    repository d'import utilisateur.
  - Le reset utilise donc actuellement le meme statut que l'import utilisateur
    si le statut est ajoute directement dans `insert` sans parametre de
    contexte.

### Reset Et Verrouillage

- `SqlAlchemyUserCollectionImportRepository.GLOBAL_GAME_IMPORT_LOCK_KEY`
  serialise le matching, la creation et les corrections de jeux globaux.
- `SqlAlchemyGameDuplicateRepository.GLOBAL_GAME_IMPORT_LOCK_KEY` reutilise la
  meme valeur pour les corrections de doublons.
- Les endpoints d'import utilisateur sont rejetes pendant un reset via
  `UserCollectionImportController._reject_when_library_reset_running`.
- `LibraryResetRepository.clean_library_tables` supprime `t_user_collection`,
  `t_game`, `t_studio`, `t_platform_image`, `t_platform_alias`, `t_platform`,
  puis restaure les images de plateformes apres reconstruction.

### Moderation Et Notifications Existantes

- Images de plateformes :
  - `PlatformImageService.upload_image` cree une image avec
    `WAITING_VALIDATION`.
  - `PlatformImageService.update_image_status` accepte ou refuse.
  - Le refus supprime la ligne et le fichier, sans statut `REFUSED`.
  - `PlatformImageAdminNotifier` notifie les admins lors d'une proposition.
- Doublons :
  - `GameDuplicateDailyNotificationService.notify_if_duplicates_exist` compte
    les jeux `duplicate_flag = TRUE`.
  - `GameDuplicateDailyNotificationScheduler` planifie une verification
    quotidienne.
  - Template existant :
    `backend/resources/game_duplicate_daily_notification_template.txt`.
  - La nouvelle notification quotidienne des jeux a valider peut suivre ce
    pattern, soit en etendant le service planifie pour executer plusieurs
    notifications admin, soit en composant un service dedie appele par le meme
    scheduler.

### Pagination, Filtres, Route Catalog Et Batch Update

- `LibraryQueryParser` normalise `page`, `size`, `sort`, `name`, `platform` et
  `duplicate_flag`.
- `LibraryQuerySqlBuilder` centralise les fragments SQL de pagination, tri et
  recherche accent-insensible.
- Les routes admin sont exposees par `/api/routes` et consommees par
  `BackendRouteAccessService`.
- Le pattern batch existant le plus proche est cote doublons pour les
  transactions globales, mais il n'existe pas encore de validation/refus par
  lots de jeux. Le futur repository devra utiliser des updates/deletes par
  blocs de 500 maximum.

## Cartographie Frontend

### Liste `/bibliotheque/jeux`

- `frontend/src/hooks/library/useLibraryGames.js`
  - Configure les colonnes `name`, `release_date`, `developer`, `editor`,
    `platform`, `status`.
  - Charge les plateformes pour le filtre plateforme.
  - Expose le filtre `duplicate_flag` uniquement pour `ADMIN`.
  - Utilise `useLibraryEntityList` pour recherche, pagination et tri serveur.
- `frontend/src/components/LibraryEntityListView.jsx`
  - Affiche le formulaire de recherche, filtre plateforme, filtre doublon, puis
    `TableComponent`.
  - Aucun filtre de statut de validation n'existe encore.
- `frontend/src/services/LibraryApi.js`
  - `fetchGames` envoie deja un Bearer optionnel frais.
  - `buildListUrl` sait encoder `duplicate_flag`; il faudra ajouter le critere
    `status`.

### Detail Public Et Acces Depuis Collection

- `frontend/src/hooks/games/useGameDetailPage.js`
  - Source `library` : appelle `LibraryApi.fetchGame(gameId)` sans Bearer.
  - Source `collection` : appelle `VideoGamesApi.fetchGame(gameId)`.
  - Pour une page detail Bibliotheque, le hook verifie ensuite l'appartenance a
    la collection via l'endpoint protege collection si la session est `USER`.
- `backend/controllers/collection_controller.py` et
  `UserCollectionQueryService.get_game` permettent deja de consulter un jeu
  rattache a la collection, independamment de la future visibilite publique.

### Menu Principal Et Visibilite Bibliotheque

- `frontend/src/components/MainMenu.jsx`
  - L'entree `Bibliotheque` est toujours visible.
  - Aucun badge/compteur n'est prevu sur cette entree.
- `documentation/menu.md` impose de propager tout changement de menu dans la
  chaine view-model, `PageLayout`, pages routees et tests.

### Configuration Et Actions Admin

- `frontend/src/components/ConfigurationView.jsx`
  - Expose deja reset Bibliotheque, import CSV admin, sync plateforme, moderation
    images, gestion utilisateurs.
- `frontend/src/hooks/library/useLibraryResetAction.js`
  - Affiche une confirmation statique avant reset.
  - Ne charge pas encore de compteur de jeux `WAITING_VALIDATION`.
- `frontend/src/services/LibraryAdminApi.js`
  - Contient les appels admin existants.
  - Devra recevoir les appels de resume compteur, validation et refus par lots.
- `frontend/src/services/BackendRouteAccessService.js`
  - Devra exposer les droits des nouveaux endpoints admin avant affichage des
    actions frontend.

### Composants De Tableau Et Selection En Masse

- `TableComponent` est le composant pagine partage.
- La selection en masse n'est pas deja generalisee dans la liste Bibliotheque
  jeux. Le workflow de moderation jeux devra soit etendre proprement la liste
  admin jeux, soit introduire un petit composant de selection/action specialise
  en gardant la pagination serveur.

## Architecture Cible Proposee

### Base De Donnees

- Ajouter `t_game.status VARCHAR(32) NOT NULL DEFAULT 'ACCEPTED'`.
- Ajouter une contrainte check :
  `status IN ('WAITING_VALIDATION', 'ACCEPTED')`.
- Ajouter un index `ix_t_game_status` pour filtrer les listes publiques/admin.
- La migration doit initialiser les lignes existantes a `ACCEPTED`.
- Mettre a jour `Game` et `documentation/database.md`.

### Contrat Backend De Visibilite

- Introduire un contexte de consultation Bibliotheque jeux contenant :
  - profil optionnel : anonyme, `GUEST`, `USER`, `ADMIN` ;
  - `current_user_id` optionnel pour `USER` ;
  - droit admin de voir tous les statuts.
- `GET /api/library/games` :
  - anonyme, `GUEST`, `USER` : uniquement `ACCEPTED` ;
  - `ADMIN` : tous les statuts, avec filtre optionnel `status`.
- `GET /api/library/games/<game_id>` :
  - anonyme : seulement `ACCEPTED` ;
  - `GUEST` : seulement `ACCEPTED` ;
  - `USER` : `ACCEPTED`, ou `WAITING_VALIDATION` si `t_user_collection`
    contient ce `game_id` pour l'utilisateur connecte ;
  - `ADMIN` : tous les statuts.
- Les compteurs Bibliotheque publics et `total_games` des plateformes doivent
  compter uniquement les jeux `ACCEPTED`, sauf compteur/admin explicitement
  documente.
- Les endpoints collection ne doivent pas filtrer `t_game.status`.

### Creation Selon Contexte

- Eviter de coder le statut en dur dans `SqlAlchemyGameRepository.insert`.
- Ajouter un parametre explicite, par exemple
  `initial_validation_status: str = "WAITING_VALIDATION"` ou un petit enum
  domaine, puis le passer depuis les orchestrateurs :
  - repository import utilisateur : `WAITING_VALIDATION` ;
  - repository import admin : `ACCEPTED` ;
  - import service utilise par reset : `ACCEPTED`.
- Le matching existant doit continuer a charger tous les jeux, quel que soit le
  statut.

### Moderation Admin Jeux

Endpoints proposes, tous `ADMIN` :

- `GET /api/library/games/validation-summary`
  - retourne au minimum `{ "waiting_validation_games": 12 }`.
  - reutilisable par le badge menu, le message reset et la notification.
- `POST /api/library/games/validation/accept`
  - payload : `{ "game_ids": [1, 2, 3] }`.
  - update par blocs de 500 vers `ACCEPTED`.
  - transactionnel.
- `POST /api/library/games/validation/refuse`
  - payload : `{ "game_ids": [1, 2, 3] }`.
  - collecte les utilisateurs impactes et jeux refuses.
  - supprime les associations `t_user_collection` puis les jeux.
  - transactionnel cote base : aucune suppression partielle en cas d'erreur.
  - envoie ensuite un email par utilisateur impacte avec template dedie.

Le refus ne doit pas persister de statut `REFUSED`, par coherence avec la
moderation d'images et le besoin exprime.

### Notification Admin Quotidienne

- Creer un template, par exemple
  `backend/resources/game_validation_daily_notification_template.txt`.
- Sujet propose : `Jeux a valider dans la Bibliotheque`.
- Corps requis :
  - nombre de jeux a valider ;
  - lien vers `${FRONTEND_PUBLIC_URL}/bibliotheque/jeux?status=WAITING_VALIDATION`.
- Reutiliser la planification quotidienne existante. Le nom
  `GameDuplicateDailyNotificationScheduler` est tres specifique ; deux options
  sont possibles :
  - option minimale : etendre le service appele par ce scheduler pour executer
    aussi la notification de validation ;
  - option plus propre : renommer/factoriser vers un scheduler admin quotidien
    generique, en gardant la configuration horaire existante.

La seconde option est plus propre mais change davantage de noms ; elle doit
etre traitee prudemment pour limiter le bruit.

### Frontend Admin

- Ajouter `status` dans `LibraryApi.buildListUrl`.
- Dans `useLibraryGames`, ajouter un filtre de statut visible seulement pour
  `ADMIN`.
- Ajouter des actions de selection/validation/refus pour les jeux
  `WAITING_VALIDATION`, probablement dans le domaine `hooks/library`.
- Ajouter le compteur admin via `LibraryAdminApi`, puis le propager :
  `BackendRouteAccessService` -> hook app/view model -> `PageLayout` ->
  `MainMenu`.
- Le badge menu doit rester informatif et ne doit pas rendre la Bibliotheque
  privee.
- Modifier `useLibraryResetAction` pour charger le compteur et enrichir le
  message de confirmation quand il est superieur a zero.

## Decisions De Contrat Encore Necessaires

- Nom du champ confirme : `t_game.status`.
- Valeurs confirmees : `WAITING_VALIDATION`, `ACCEPTED`.
- Statut migration confirme : `ACCEPTED`.
- Strategie de refus confirmee par le besoin : suppression du jeu et
  desassociation de `t_user_collection`.
- Decision a confirmer : les emails de refus sont-ils envoyes apres commit
  transactionnel, avec journalisation des echecs email, ou l'echec email doit-il
  annuler la transaction SQL ? Le besoin dit que les suppressions sont
  transactionnelles ; il ne precise pas si l'envoi mail fait partie de la meme
  unite atomique. Recommandation : commit SQL d'abord, puis emails, pour eviter
  qu'un incident SMTP conserve des jeux refuses.
- Decision a confirmer : le filtre `status` envoye par un non-ADMIN doit-il etre
  ignore ou retourner `403/400` ? Recommandation : ignorer cote backend pour la
  liste publique et ne jamais exposer `WAITING_VALIDATION`.
- Decision a confirmer : `GUEST` proprietaire via partage ne doit pas voir les
  jeux `WAITING_VALIDATION` dans la Bibliotheque publique, mais continue de les
  voir via les routes collection partagees si le jeu est dans la collection du
  proprietaire. Cela respecte le besoin qui reserve l'exception Bibliotheque au
  `USER` proprietaire connecte.

## Risques Et Conflits Documentaires

- `documentation/bibliotheque.md`
  - Concerne. La doc dit que la Bibliotheque publique lit `t_game` et que les
    routes publiques sont read-only. Le nouveau filtre `ACCEPTED` respecte la
    consultation publique, mais les nouveaux endpoints admin d'ecriture doivent
    etre ajoutes comme exceptions protegees.
- `documentation/backend-api.md`
  - Concerne. Les routes, payloads, droits, statuts HTTP et query params doivent
    etre documentes.
- `documentation/database.md`
  - Concerne. Ajout de colonne, check et index sur `t_game`.
- `documentation/site-plan.md`
  - Concerne. La page `/bibliotheque/jeux` gagne un filtre admin, badge menu et
    actions admin.
- `documentation/authentication.md`
  - Concerne. Le detail public jeux devient dependant d'un Bearer optionnel
    pour l'exception `USER` proprietaire, et les nouveaux endpoints admin
    doivent etre ajoutes.
- `documentation/backend-arch.md`
  - Concerne. La solution doit garder HTTP dans les controleurs, logique dans
    les services, SQL dans les repositories, et continuer a utiliser le verrou
    global pour les workflows qui modifient les jeux globaux.
- `documentation/frontend-arch.md`
  - Concerne. Les appels admin restent dans `LibraryAdminApi`, l'etat dans les
    hooks `hooks/library`, les composants rendent seulement l'UI.
- `documentation/menu.md`
  - Concerne. Le badge Bibliotheque impose une propagation complete et un test
    frontend de regression.

## Fichiers Probablement Concernés

### Backend

- `backend/services/database/game.py`
- `backend/migrations/versions/<new>_add_game_validation_status.py`
- `backend/services/database/database_schema_service.py` si le schema initial
  manuel contient encore la definition des tables.
- `backend/services/database/game_repository.py`
- `backend/services/library/library_query_contract.py`
- `backend/services/library/library_service.py`
- `backend/services/library/library_payload_serializer.py`
- `backend/controllers/game_controller.py`
- `backend/controllers/library_controller.py`
- `backend/services/database/user_collection_import_repository.py`
- `backend/services/database/admin_library_import_repository.py`
- `backend/services/library/library_reset_service.py`
- `backend/services/database/library_reset_repository.py`
- Nouveaux fichiers probables :
  - service de moderation jeux ;
  - repository de moderation jeux ;
  - service de notification quotidienne jeux a valider ;
  - template email quotidien ;
  - template email utilisateur de refus.

### Frontend

- `frontend/src/services/LibraryApi.js`
- `frontend/src/services/LibraryAdminApi.js`
- `frontend/src/services/BackendRouteAccessService.js`
- `frontend/src/hooks/library/useLibraryGames.js`
- `frontend/src/hooks/library/useLibraryResetAction.js`
- `frontend/src/hooks/app/useCloudCollectionViewModel.js`
- `frontend/src/components/LibraryEntityListView.jsx`
- `frontend/src/components/MainMenu.jsx`
- `frontend/src/components/PageLayout.jsx`
- `frontend/src/components/AppViewSwitch.jsx`
- `frontend/src/components/ConfigurationView.jsx`
- CSS existant sous `frontend/src/styles/`, probablement `library.css`,
  `admin.css` ou `styles.css`.

### Documentation

- `documentation/bibliotheque.md`
- `documentation/backend-api.md`
- `documentation/database.md`
- `documentation/site-plan.md`
- `documentation/authentication.md`
- `README.md` seulement si les routes, commandes ou comportements exposes aux
  utilisateurs/admins doivent etre resumes.

## Tests Backend A Creer Ou Modifier

- `backend/tests/by_module/services/database/test_database_schema_service.py`
  ou tests migration/schema : colonne, check et index `t_game.status`.
- `backend/tests/by_module/services/database/test_game_repository.py` :
  insertion avec statut explicite, filtrage liste/detail, matching tous statuts.
- `backend/tests/by_module/services/library/test_library_service.py` :
  visibilite `ACCEPTED`, admin tous statuts, detail `USER` proprietaire.
- `backend/tests/by_module/controllers/test_library_routes.py` :
  contrats HTTP liste/detail par profil et Bearer optionnel.
- `backend/tests/by_module/services/users/test_user_collection_import_service.py`
  ou repository d'import : nouveaux jeux utilisateur en `WAITING_VALIDATION`.
- `backend/tests/by_module/services/library/test_admin_library_import_service.py` :
  nouveaux jeux admin en `ACCEPTED`.
- `backend/tests/by_module/services/library/test_library_reset_service.py` :
  reset recreant les jeux en `ACCEPTED`.
- Nouveaux tests de moderation jeux :
  - acceptation par lots et blocs de 500 ;
  - refus transactionnel ;
  - collecte des utilisateurs impactes ;
  - suppression des associations ;
  - route catalog et droits `ADMIN`.
- Tests notification quotidienne :
  - pas d'email si compteur zero ;
  - email admin template avec lien filtre statut ;
  - execution via le scheduler quotidien existant ou factorise.

## Tests Frontend A Creer Ou Modifier

- `frontend/tests/libraryGamesCollectionMarker.test.js` ou nouveau test de liste
  Bibliotheque :
  - filtre statut visible seulement `ADMIN` ;
  - query string `status=WAITING_VALIDATION` envoyee par `LibraryApi`.
- Tests `BackendRouteAccessService` :
  - nouveaux droits admin moderation jeux et compteur.
- Tests menu/navigation :
  - badge Bibliotheque propage par les pages routees via `PageLayout`.
- Tests reset :
  - confirmation avec message additionnel quand compteur `WAITING_VALIDATION`
    > 0.
- Tests actions de masse :
  - selection, validation, refus, refresh de liste et erreurs.

## Validation Et Ordre De Realisation Recommande

1. Ajouter le schema et le modele `status`.
2. Rendre le statut initial explicite dans le coeur d'import et ses contextes.
3. Filtrer les lectures publiques et ajouter l'acces detail `USER`
   proprietaire.
4. Ajouter les endpoints admin de moderation par lots et le compteur.
5. Ajouter notification quotidienne et templates email.
6. Ajouter le workflow frontend admin.
7. Mettre a jour les documentations concernees apres confirmation.
8. Executer `./scripts/test_backend.sh`, `npm test` depuis `frontend`, puis
   rebuild Docker car le comportement runtime backend/frontend change.

## Conclusion

Les criteres d'acceptation de la tache 00 sont satisfaits par ce rapport :

- le rapport existe ;
- aucun code applicatif n'a ete modifie ;
- les sous-taches suivantes disposent de la cartographie et des contrats cibles
  necessaires.
