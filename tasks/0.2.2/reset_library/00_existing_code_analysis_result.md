# Analyse existante et contrat reset Bibliotheque

## Synthese

La fonctionnalite demandee est realisable sans nouveau framework ni nouvelle
dependance. Elle doit s'appuyer sur les couches existantes :

- controleur HTTP sous `backend/controllers/` ;
- orchestration metier sous `backend/services/library/` ;
- persistance SQL sous `backend/services/database/` ;
- import utilisateur existant via `UserCollectionImportService` ;
- email applicatif existant via `EmailSenderFactory` et `ADMIN_NOTIFICATION_EMAIL` ;
- frontend Configuration existant avec un service API et un hook dedie.

Le changement introduit une exception importante aux regles actuelles :
les routes publiques de consultation Bibliotheque restent publiques et read-only,
mais un nouvel endpoint protege `ADMIN` permet de reconstruire les donnees
globales. Cette exception doit etre documentee explicitement dans
`documentation/bibliotheque.md`, `documentation/backend-api.md` et
`documentation/site-plan.md`.

## Documentation lue

- `documentation/backend-arch.md` : les endpoints restent dans les controleurs,
  la logique metier dans les services et la persistance dans les repositories.
- `documentation/backend-api.md` : les routes applicatives sont protegees sauf
  exceptions publiques ; les routes Bibliotheque actuelles sont publiques.
- `documentation/bibliotheque.md` : les consultations Bibliotheque sont publiques
  et read-only. Le reset admin doit devenir une exception documentee.
- `documentation/import.md` : l'import utilisateur est autoritaire cote backend,
  reutilisable, transactionnel par import et expose les routes a bloquer pendant
  reset.
- `documentation/site-plan.md` : `/configuration` est la page des actions
  protegees ; `ADMIN` ne doit pas utiliser les ecrans de collection utilisateur.
- `documentation/database.md` : les relations imposent de supprimer
  `t_user_collection`, puis `t_game`, puis `t_studio` et `t_platform`.
- `documentation/frontend-arch.md` : les appels HTTP restent dans
  `frontend/src/services/`, l'orchestration dans `frontend/src/hooks/`, et les
  pages ne portent que le rendu/interactions.
- `documentation/menu.md` : aucun changement de menu n'est requis pour cette
  tache.

## Fichiers existants a modifier

### Backend

- `backend/app.py`
  - instancier le nouveau controleur ;
  - partager le coordinateur de reset avec le controleur d'import utilisateur ;
  - enregistrer la route avant `AuthGuard.protect_all_routes`.
- `backend/controllers/__init__.py`
  - exporter le nouveau controleur.
- `backend/controllers/library_controller.py` ou nom equivalent
  - nouveau fichier conseille pour `POST /api/library/reset` ;
  - utiliser `AuthGuard.require_profile(UserProfile.ADMIN.value)`.
- `backend/controllers/user_collection_import_controller.py`
  - refuser les routes d'import pendant un reset actif.
- `backend/services/library/`
  - ajouter un coordinateur de job asynchrone en memoire ;
  - ajouter un service d'orchestration du reset global ;
  - ajouter un contexte de job contenant succes et erreurs.
- `backend/services/database/`
  - ajouter un repository de reset Bibliotheque ou etendre prudemment un
    repository existant ;
  - ajouter la lecture des utilisateurs importables ;
  - ajouter le clean transactionnel des tables globales.
- `backend/services/__init__.py`
  - exporter les nouveaux services si les patterns de composition en ont besoin.
- `backend/tests/`
  - ajouter ou mettre a jour les tests de routes, service, repository et
    verrouillage import.

### Frontend

- `frontend/src/services/LibraryApi.js`
  - soit ajouter `resetLibrary()` avec headers Bearer ;
  - soit creer un service separe si l'on veut conserver `LibraryApi` strictement
    public. Le service separe est preferable pour ne pas melanger public read-only
    et action admin destructive.
- `frontend/src/hooks/`
  - ajouter un hook dedie au reset Bibliotheque admin, par exemple
    `hooks/library/useLibraryReset.js` ou `hooks/configuration/useLibraryReset.js`.
- `frontend/src/hooks/app/useCloudCollectionViewModel.js`
  - composer le hook et exposer etat/callback a la page Configuration.
- `frontend/src/components/AppViewSwitch.jsx`
  - transmettre les nouvelles props a `ConfigurationView`.
- `frontend/src/components/ConfigurationView.jsx`
  - ajouter un encart visible uniquement pour `ADMIN`.
- `frontend/src/services/BackendRouteAccessService.js`
  - ajouter la permission `canResetLibrary` basee sur
    `POST /api/library/reset`.

### Documentation

- `documentation/backend-api.md`
- `documentation/bibliotheque.md`
- `documentation/import.md`
- `documentation/site-plan.md`
- `documentation/database.md` a verifier, mais aucune migration n'est attendue
  si la structure ne change pas.
- `README.md` a verifier, surtout pour rappeler `ADMIN_NOTIFICATION_EMAIL` si le
  reset l'utilise aussi.

## Patterns existants a reutiliser

- Protection de route admin : `UserController` utilise
  `auth_guard.require_profile(UserProfile.ADMIN.value)`.
- Protection globale : `AuthGuard.protect_all_routes` marque toutes les routes
  non publiques et expose les metadonnees via `/api/routes`.
- Controleurs Bibliotheque : les routes publiques actuelles sont dans
  `PlatformController`, `StudioController` et `GameController`. Le reset doit
  rester separe dans un nouveau controleur pour eviter de melanger consultation
  publique et action destructive.
- Import utilisateur : `UserCollectionImportService.import_collection(...)`
  accepte un `user_id`, un chemin de fichier source, un nom de fichier et une
  `CollectionFileDescription`. C'est le point de reutilisation a privilegier
  pour chaque utilisateur pendant le reset.
- Validation de configuration : `CollectionFileDescriptionValidator.validate(...)`
  convertit le JSON sauvegarde en objet metier attendu par le service d'import.
- Verrou par utilisateur : `UserCollectionImportService` possede deja un verrou
  par `user_id`. Le reset global doit ajouter un verrou global separe.
- Email : `EmailSenderFactory.create(EmailConfiguration.from_environment())`
  existe et `ADMIN_NOTIFICATION_EMAIL` est deja utilise pour notifier
  l'administrateur lors des inscriptions.
- Frontend Configuration : `ConfigurationView` affiche deja des cartes
  conditionnees par profil et permissions. Le reset admin peut reprendre ce
  format avec un message de confirmation plus fort.
- Erreurs frontend collection : `UserCollectionApi` normalise les erreurs HTTP.
  Pour le reset Bibliotheque, creer une erreur typee similaire ou un traitement
  simple dans un service admin dedie.

## Contrat final de `POST /api/library/reset`

- Methode : `POST`.
- Route : `/api/library/reset`.
- Authentification : Bearer token obligatoire.
- Autorisation : profil `ADMIN` uniquement.
- Corps de requete : aucun.
- Succes :

```http
202 Accepted
Content-Type: application/json
```

```json
{
  "job_id": 25
}
```

- Conflit :

```http
409 Conflict
Content-Type: application/json
```

```json
{
  "error": "Un reset de la Bibliotheque est deja en cours."
}
```

- Pas d'endpoint de statut pour cette version.
- Le suivi se fait par logs backend et par email final envoye a
  `ADMIN_NOTIFICATION_EMAIL`.
- L'endpoint doit apparaitre dans `/api/routes` avec :
  - `requires_auth: true` ;
  - `auth_schemes: ["Bearer"]` ;
  - `required_profiles: ["ADMIN"]`.

## Contrat du job asynchrone

Le coordinateur de job doit etre en memoire pour cette version.

Etat minimal conseille :

- `job_id` incremental ;
- `running` ou equivalent pour bloquer un second reset ;
- `started_at` ;
- `finished_at` ;
- listes en memoire :
  - utilisateurs importes avec succes ;
  - utilisateurs ignores ;
  - erreurs par utilisateur ;
  - erreur globale de clean base si presente.

Le contexte en memoire sert uniquement pendant l'execution du job et pour
composer le mail final. Il n'y a pas de persistance du statut ni d'endpoint de
consultation.

## Orchestration backend attendue

1. Refuser le lancement si un reset est deja en cours.
2. Creer un `job_id`.
3. Demarrer le traitement asynchrone et retourner `202`.
4. Dans le job :
   - nettoyer la base dans une transaction ;
   - si le clean echoue, rollback, enregistrer l'erreur globale, arreter le job
     et envoyer le mail final ;
   - charger les utilisateurs importables ;
   - traiter les utilisateurs dans l'ordre de `t_user.creation_date` ;
   - valider que le fichier existe et est lisible ;
   - valider que `collection_file_description` est non vide ;
   - parser `collection_file_description` via le validateur existant ;
   - appeler le service d'import existant avec le fichier final de l'utilisateur ;
   - enregistrer les succes et erreurs dans le contexte ;
   - continuer avec l'utilisateur suivant en cas d'echec utilisateur ;
   - envoyer un mail final a `ADMIN_NOTIFICATION_EMAIL`.
5. Liberer le verrou global dans tous les cas.

## Repository de reset Bibliotheque

Un nouveau repository dedie est conseille, par exemple
`SqlAlchemyLibraryResetRepository`, afin de ne pas gonfler
`SqlAlchemyUserCollectionImportRepository`.

Responsabilites conseillees :

- `clean_library_tables()` :
  - ouvrir `engine.begin()` ;
  - supprimer dans l'ordre :
    1. `t_user_collection` ;
    2. `t_game` ;
    3. `t_studio` ;
    4. `t_platform` ;
  - laisser SQLAlchemy rollback automatiquement en cas d'exception.
- `list_importable_users()` :
  - lire les utilisateurs ayant `collection_file_path IS NOT NULL` ;
  - ordonner par `creation_date ASC`, puis `id ASC` pour stabiliser l'ordre ;
  - retourner au minimum `id`, `email`, `collection_file_path`,
    `collection_file_description`, `profile`, `status`, `creation_date`.

Le contrat de la tache ne filtre pas explicitement par profil ou statut. Pour
eviter une interpretation implicite, l'implementation initiale doit suivre le
texte : tous les utilisateurs avec `collection_file_path` renseigne. Si un
filtre `profile='USER'` ou `status='ACTIVE'` est souhaite, il faut le faire
confirmer avant de coder.

## Endpoints d'import a bloquer pendant reset

Les endpoints suivants doivent retourner `403 Forbidden` si un reset global est
en cours :

- `POST /api/users/import/file/<file_type>` ;
- `POST /api/users/import/analyze/<file_type>` ;
- `POST /api/users/import` ;
- `GET /api/users/import/` ;
- `POST /api/users/collection/reinit`.

Message JSON propose :

```json
{
  "error": "Un reset de la Bibliotheque est en cours. Veuillez reessayer plus tard."
}
```

`GET /api/users/me/collection` n'est pas liste dans la tache comme endpoint
d'import a bloquer. Il peut rester disponible car il sert a la navigation et ne
modifie pas les donnees.

## Contraintes et risques identifies

- Le reset vide `t_user_collection` pour tous les utilisateurs. Les imports
  reussis reconstruisent les associations ; les imports echoues laissent les
  utilisateurs sans collection SQL jusqu'a correction.
- Le champ `t_user.collection_file_path` ne doit pas etre efface pendant le
  reset global : il sert de source pour reimporter.
- Le service `UserCollectionImportService.import_collection(...)` copie le fichier
  source vers le chemin cible de l'utilisateur. Si le chemin source est deja le
  chemin cible, il faut verifier le comportement de copie. Une adaptation peut
  etre necessaire pour importer depuis le fichier stocke sans l'effacer ni le
  recopier inutilement.
- Le service d'import existant est transactionnel par utilisateur. Le reset
  global n'est pas transactionnel apres clean reussi : les erreurs utilisateurs
  produisent volontairement une reconstruction partielle.
- L'envoi d'email final ne doit pas masquer la fin du job : si l'email echoue,
  l'erreur doit etre logguee et le verrou global doit etre libere.
- Un coordinateur en memoire ne survit pas a un redemarrage backend. C'est
  conforme a la tache car aucun endpoint de statut ni persistance de job n'est
  demande.

## Tests a creer ou modifier

### Routes backend

- `POST /api/library/reset` sans token retourne le refus d'authentification
  existant.
- `POST /api/library/reset` avec profil `USER` retourne `403`.
- `POST /api/library/reset` avec profil `ADMIN` retourne `202` et un `job_id`.
- Second appel pendant un reset retourne `409`.
- `/api/routes` declare `POST /api/library/reset` protege et reserve `ADMIN`.

### Service de job

- Le coordinateur cree des `job_id` stables et refuse un lancement concurrent.
- Le verrou global est libere apres succes.
- Le verrou global est libere apres exception.
- Le contexte contient succes, erreurs utilisateur et erreur globale.

### Repository reset

- Le clean supprime dans l'ordre `t_user_collection`, `t_game`, `t_studio`,
  `t_platform`.
- Le clean rollback si une suppression echoue.
- La lecture des utilisateurs importables filtre `collection_file_path IS NOT NULL`
  et ordonne par `creation_date`, puis `id`.

### Orchestration import

- Fichier absent : erreur utilisateur en contexte, traitement du suivant.
- Fichier illisible : erreur utilisateur en contexte, traitement du suivant.
- `collection_file_description` null ou vide : erreur utilisateur en contexte,
  traitement du suivant.
- Configuration invalide : erreur utilisateur en contexte, traitement du suivant.
- Echec d'import : erreur utilisateur en contexte, traitement du suivant.
- Succes partiel : mail final indiquant succes et erreurs.
- Echec de clean : aucun import utilisateur lance et mail final indiquant
  l'erreur globale.

### Blocage import

- Chaque endpoint liste dans la section "Endpoints d'import a bloquer" retourne
  `403` pendant reset.
- Les memes endpoints gardent leur comportement existant hors reset.

### Frontend

- La carte reset Bibliotheque est visible uniquement pour `ADMIN`.
- La carte n'est pas visible pour `USER`.
- La confirmation est demandee avant appel backend.
- `202` affiche un message "reset en cours".
- `409` affiche un message "reset deja en cours".
- Le build frontend passe.

## Documentation impactee

- `documentation/backend-api.md` : ajouter le contrat `POST /api/library/reset`,
  les erreurs `202`, `403`, `409`, et le refus des imports pendant reset.
- `documentation/bibliotheque.md` : conserver la consultation publique read-only
  et ajouter l'exception admin protegee pour reset.
- `documentation/import.md` : documenter le refus `403` des routes d'import
  pendant un reset global.
- `documentation/site-plan.md` : documenter l'encart `ADMIN` dans Configuration.
- `documentation/database.md` : verifier si une mise a jour est necessaire. Aucune
  migration n'est attendue si aucune table/colonne n'est ajoutee.
- `README.md` : verifier si `ADMIN_NOTIFICATION_EMAIL` doit mentionner aussi les
  notifications de reset Bibliotheque.

## Decision d'architecture proposee

Le reset doit etre implemente comme une fonctionnalite d'administration de la
Bibliotheque, pas comme une extension des routes publiques existantes :

- nouveau `LibraryController` pour `POST /api/library/reset` ;
- nouveau service sous `backend/services/library/` pour le job global ;
- nouveau repository SQL dedie au reset ;
- reutilisation stricte de `UserCollectionImportService` pour reconstruire les
  donnees ;
- injection du coordinateur global dans le controleur d'import utilisateur pour
  centraliser le blocage `403`.

Cette approche respecte les limites de couches du projet et evite de dupliquer
la logique metier d'import.
