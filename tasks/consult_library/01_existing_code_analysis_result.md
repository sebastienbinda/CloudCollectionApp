# 01 - Rapport d'analyse du code existant

## Synthese

La fonctionnalite Bibliotheque peut etre developpee sans changement de schema
identifie a ce stade. Les tables globales existent deja pour les plateformes,
studios et jeux. La fonctionnalite doit ajouter une couche de consultation
publique en lecture seule, distincte des workflows ODS et collection utilisateur.

Les routes Bibliotheque doivent rester publiques, ne pas exposer de donnees
utilisateur, et lire uniquement les tables globales de reference.

## Documentation lue

- `documentation/backend-arch.md`
- `documentation/frontend-arch.md`
- `documentation/backend-api.md`
- `documentation/site-plan.md`
- `documentation/menu.md`
- `documentation/database.md`
- `tasks/consult_library/consult.md`
- `tasks/consult_library/00_backend_developer_naming_cleanup.md`

## Modeles backend existants

### Plateformes

Fichier : `backend/services/database/platform.py`

Modele ORM : `Platform`

Champs utiles :
- `id`
- `name`
- `release_date`
- `manufacturer`
- `description`
- `status`

Le contrat de `consult.md` est maintenant aligne avec ces champs pour la liste
des plateformes. Le champ `description` est structure en `JSONB` et devra etre
serialise tel quel ou normalise explicitement par le service.

### Studios

Fichier : `backend/services/database/studio.py`

Modele ORM : `Studio`

Champs utiles :
- `id`
- `name`
- `country`
- `city`
- `creation_date`
- `status`

Le contrat de `consult.md` est maintenant aligne avec ces champs pour la liste
des studios.

### Jeux

Fichier : `backend/services/database/game.py`

Modele ORM : `Game`

Champs utiles :
- `id`
- `name`
- `release_date`
- `developper`
- `editor`
- `platform`
- `description`

Point d'attention bloquant : le champ ORM existant est `developper` avec deux
`p`. La regle cible est d'utiliser l'orthographe anglaise correcte
`developer` partout. L'existant doit donc etre corrige par la tache
`00_backend_developer_naming_cleanup.md` avant d'implementer les endpoints
Bibliotheque.

## Repositories backend existants

### `SqlAlchemyPlatformRepository`

Fichier : `backend/services/database/platform_repository.py`

Responsabilite actuelle :
- charger les identifiants de plateformes par cle normalisee ;
- inserer une plateforme absente pendant l'import.

Methodes a ajouter pour la Bibliotheque :
- comptage global des plateformes ;
- lecture paginee avec recherche, tri et `total_games`.

Limite actuelle :
- ne contient pas de lecture paginee ;
- ne calcule pas `total_games` ;
- ne gere ni recherche, ni tri public.

Conclusion : etendre ce repository d'entite existant. Les nouvelles methodes
doivent etre clairement nommees pour la consultation publique et rester
separees des methodes d'import.

### `SqlAlchemyStudioRepository`

Fichier : `backend/services/database/studio_repository.py`

Responsabilite actuelle :
- charger les identifiants de studios par cle normalisee ;
- inserer un studio absent pendant l'import.

Methodes a ajouter pour la Bibliotheque :
- comptage global des studios ;
- lecture paginee avec recherche, tri, `editor_total_games` et
  `developer_total_games`.

Limite actuelle :
- ne contient pas de lecture paginee ;
- ne calcule pas `editor_total_games` ni `developer_total_games`.

Conclusion : etendre ce repository d'entite existant avec des methodes de
consultation publique dediees.

### `SqlAlchemyGameRepository`

Fichier : `backend/services/database/game_repository.py`

Responsabilite actuelle :
- charger les identifiants de jeux par cle plateforme/nom ;
- inserer un jeu absent pendant l'import.

Methodes a ajouter pour la Bibliotheque :
- comptage global des jeux ;
- lecture paginee avec recherche, tri, nom du developpeur, nom de l'editeur et
  nom de la plateforme.

Limite actuelle :
- ne contient pas de lecture paginee ;
- ne joint pas les noms de developpeur, editeur et plateforme pour une API de
  consultation.
- utilise encore la colonne SQL `developper`, a corriger vers `developer`.

Conclusion : etendre ce repository d'entite existant avec des methodes de
consultation publique dediees, apres correction du nommage `developer`.

## Services backend reutilisables

### Normalisation des noms

Fichier : `backend/services/users/user_collection_name_normalizer.py`

Classe : `UserCollectionNameNormalizer`

La methode `comparison_key` supprime les accents et neutralise la casse. Elle
peut etre reutilisee pour preparer une recherche contains sans casse et sans
accents, ou servir de reference comportementale pour un utilitaire SQL dedie.

Point d'attention : pour une recherche SQL performante et paginee, il faudra
probablement appliquer la normalisation cote requete, par exemple via une
expression SQL compatible PostgreSQL, plutot que filtrer en memoire.

### Configuration base

Fichier : `backend/services/database/database_configuration.py`

Classe : `DatabaseConfiguration`

Elle fournit `database_url` et `schema_name`. Les nouveaux repositories de
consultation doivent suivre ce pattern et ne pas hardcoder le schema.

## Controleurs backend existants

### Pattern de controleur public/protege

Fichiers utiles :
- `backend/controllers/platform_controller.py`
- `backend/controllers/route_controller.py`
- `backend/controllers/user_collection_import_controller.py`

Les controleurs enregistrent leurs routes via `register_routes(flask_app)`.
Les routes protegees utilisent `AuthGuard`, tandis que les routes publiques sont
enregistrees sans wrapper d'authentification mais restent protegees globalement
sauf exemption.

Point important : `backend/app.py` appelle `auth_guard.protect_all_routes(...)`
avec uniquement les endpoints publics d'authentification en exemption. Pour
rendre `/api/library/*` public, il faudra etendre le mecanisme d'exemption ou
fournir une liste d'endpoints publics portee par les controleurs d'entite a
`protect_all_routes`.

Conclusion : utiliser un controleur par entite. Le controleur existant
`PlatformController` doit etre reutilise et etendu pour les plateformes avec
l'orthographe correcte `platform`. Ajouter `StudioController` et
`GameController` pour les autres entites. Ne pas creer de `LibraryController`
transverse.

## Tests backend existants

Fichiers utiles :
- `backend/tests/test_app_routes.py`
- `backend/tests/test_user_collection_name_normalizer.py`
- tests de service sous `backend/tests/`

Recommandations :
- ajouter des tests unitaires pour le parsing pagination/recherche/tri ;
- ajouter des tests de service ou repository pour les compteurs et listes ;
- ajouter des tests de routes pour verifier que `/api/library/*` repond sans
  token et ne retourne pas de champs prives.

## Frontend existant a reutiliser

### Routage

Fichiers :
- `frontend/src/appRouting.js`
- `frontend/src/hooks/navigation/useAppNavigation.js`
- `frontend/src/components/AppViewSwitch.jsx`
- `frontend/src/hooks/app/useCloudCollectionViewModel.js`

Le routage est centralise. Les nouvelles vues devront etre ajoutees dans
`AppRouting.getViewFromUrl`, `useAppNavigation`, `AppViewSwitch` et le
view-model principal.

Point d'attention : `AppRouting.isPublicPath` ne contient aujourd'hui que
`/about` et `/auth`. Les routes `/bibliotheque*` devront y etre ajoutees pour
rester accessibles sans session.

### Menu principal

Fichier : `frontend/src/components/MainMenu.jsx`

Le menu est partage entre About, Accueil et onboarding. Il recoit les callbacks
de navigation par props. L'entree Bibliotheque devra etre disponible pour tous
les visiteurs, sans condition d'authentification.

Documentation a respecter : `documentation/menu.md`.

### Cartes de la page accueil

Fichiers :
- `frontend/src/components/HomeView.jsx`
- `frontend/src/styles/home.css`

Le rendu des cartes plateformes utilise actuellement `platformGrid`,
`platformCard`, `platformCardHeader` et `platformGameCount`.

La cible demandee est de normaliser ces noms en composants reutilisables :
- `GridComponent` pour remplacer l'usage direct de `platformGrid` ;
- `CardComponent` pour remplacer l'usage direct de `platformCard` ;
- `CardHeaderComponent` pour remplacer l'usage direct de `platformCardHeader` ;
- `CardCountComponent` pour remplacer l'usage direct de `platformGameCount`.

Ces composants doivent ensuite etre utilises par la page accueil et par la page
Bibliotheque. Les styles existants peuvent etre migres, renommes ou aliases
temporairement, mais le point d'entree React reutilisable doit porter les noms
generiques ci-dessus.

### Tableaux

Fichier : `frontend/src/components/GameTable.jsx`

Le composant est deja reutilisable techniquement pour afficher un tableau avec
tri et filtres par colonne, mais son nom reste specifique aux jeux. La cible
demandee est de centraliser ce rendu sous un composant generique
`TableComponent`.

`TableComponent` doit devenir le point d'entree reutilisable pour :
- les tableaux de collection ;
- les tableaux de wishlist ;
- les tableaux de consultation Bibliotheque.

La migration doit preserver les capacites existantes utiles : colonnes,
libelles, tri, filtres, classes responsives et actions de ligne optionnelles.
Les besoins Bibliotheque ajoutent aussi une pagination serveur et une recherche
serveur par nom. La gestion UI de pagination doit etre centralisee dans
`TableComponent` : controles, etat disabled, affichage de page courante et
callbacks de changement de page. Les hooks conservent l'etat et les appels API,
mais les pages ne doivent pas reimplementer les controles de pagination.

Fichiers complementaires :
- `frontend/src/components/WishlistView.jsx`
- `frontend/src/components/PlatformDetailView.jsx`
- `frontend/src/styles/editorial-views.css`
- `frontend/src/styles.css`

Ces vues donnent les patterns visuels de sections, statistiques, tableaux et
actions de ligne. Pour la Bibliotheque, aucune action d'ajout, edition ou
suppression ne doit etre affichee.

### Services frontend

Fichiers :
- `frontend/src/services/JeuxVideoApi.js`
- `frontend/src/services/BackendAvailabilityGuard.js`
- `frontend/src/services/TableColumnFormatService.jsx`

Les appels API utilisent `BackendAvailabilityGuard.fetch`. Un nouveau service
dedie, par exemple `LibraryApi.js`, doit suivre ce pattern. Comme les endpoints
sont publics, il ne doit pas ajouter de headers d'authentification obligatoires.

## Fichiers probablement a creer

Backend :
- `backend/controllers/studio_controller.py`
- `backend/controllers/game_controller.py`
- `backend/services/library/` ou service equivalent de domaine Bibliotheque
- tests backend dedies sous `backend/tests/`

Frontend :
- `frontend/src/services/LibraryApi.js`
- hooks sous `frontend/src/hooks/library/`
- composants de page Bibliotheque sous `frontend/src/components/`
- composants de cartes reutilisables sous `frontend/src/components/`
- `TableComponent` sous `frontend/src/components/`
- styles dedies si les styles existants ne suffisent pas

Documentation :
- `documentation/bibliotheque.md`

## Fichiers probablement a modifier

Backend :
- `backend/app.py`
- `backend/controllers/__init__.py`
- `backend/controllers/platform_controller.py`
- `backend/services/__init__.py`
- `backend/services/database/__init__.py`
- `backend/services/database/platform_repository.py`
- `backend/services/database/studio_repository.py`
- `backend/services/database/game_repository.py`
- `backend/tests/test_app_routes.py`

Frontend :
- `frontend/src/appRouting.js`
- `frontend/src/hooks/navigation/useAppNavigation.js`
- `frontend/src/hooks/app/useCloudCollectionViewModel.js`
- `frontend/src/components/AppViewSwitch.jsx`
- `frontend/src/components/MainMenu.jsx`
- `frontend/src/components/HomeView.jsx`
- `frontend/src/components/GameTable.jsx`
- styles existants ou nouveau fichier de styles importe depuis `main.jsx`

Documentation :
- `documentation/site-plan.md`
- `documentation/backend-api.md`
- `documentation/frontend-arch.md` si un nouveau domaine de hooks est ajoute
- `documentation/backend-arch.md` si un nouveau domaine de service est ajoute
- `documentation/menu.md` si les contraintes du menu public evoluent

## Points d'attention avant implementation

1. Corriger l'existant `developper` vers `developer` avant les endpoints
   Bibliotheque.
2. Les routes publiques `/api/library/*` doivent etre ajoutees aux exemptions
   d'authentification globale.
3. Les colonnes de tri doivent rester limitees aux allowlists de `consult.md`.

## Conclusion

Le developpement Bibliotheque peut demarrer apres la correction de nommage
`developer`. La meilleure approche est ensuite de creer un domaine Bibliotheque
dedie, en lecture seule, qui orchestre les repositories d'entite existants. Les
repositories `SqlAlchemyPlatformRepository`, `SqlAlchemyStudioRepository` et
`SqlAlchemyGameRepository` doivent etre etendus avec des methodes de
consultation publique plutot que remplaces par un repository transverse.
