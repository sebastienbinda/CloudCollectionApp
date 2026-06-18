# 00 - Résultat d'analyse du code existant

## Synthèse

La fonctionnalité peut être ajoutée sans changer le paradigme général du projet.
Elle touche trois zones principales :

- la Bibliothèque publique, pour enrichir le détail plateforme et servir les
  images acceptées ;
- les actions protégées de Configuration, pour la modération administrateur ;
- l'infrastructure runtime, pour la table `t_platform_image`, le stockage disque
  et les volumes Docker.

Le point contractuel le plus important est l'exception publique à ajouter :
`GET /api/library/platforms/{platform_id}/image/{image_id}` doit être public,
mais ne doit servir que les images `ACCEPTED`. Tous les endpoints d'écriture ou
de modération restent protégés par Bearer token.

## Documentation Vérifiée

- `tasks/0.2.6/add_image_to_plateforme/add_image.md`
- `documentation/backend-api.md`
- `documentation/authentication.md`
- `documentation/backend-arch.md`
- `documentation/frontend-arch.md`
- `documentation/database.md`
- `documentation/site-plan.md`
- `documentation/menu.md`

## Cartographie Backend

### Composition Flask

`backend/app.py` est le point de composition. Il :

- construit `AuthGuard` ;
- instancie `LibraryController`, `PlatformController`, `StudioController` et
  `GameController` ;
- enregistre les routes ;
- applique `auth_guard.protect_all_routes(...)` avec les endpoints publics.

La fonctionnalité images devra ajouter un contrôleur ou étendre un contrôleur
existant avant l'appel à `protect_all_routes`. Les endpoints publics d'images
devront être ajoutés à la liste d'exemption globale.

### Routes Plateformes Publiques

`backend/controllers/platform_controller.py` porte actuellement :

- `GET /api/library/entities` ;
- `GET /api/library/platforms` ;
- `GET /api/library/platforms/<int:platform_id>`.

Ces endpoints sont déclarés publics via `PlatformController.PUBLIC_ENDPOINTS`.
Le détail plateforme appelle `LibraryService.get_platform(platform_id)`.

### Routes Admin Bibliothèque

`backend/controllers/library_controller.py` porte actuellement :

- `POST /api/library/reset`, protégé `ADMIN` ;
- `POST /api/library/platform-catalog/sync`, protégé `ADMIN`.

Ce fichier est le pattern le plus proche pour les endpoints admin de
modération. Une extension directe est possible, mais un nouveau
`PlatformImageController` est préférable pour éviter de dépasser les
responsabilités de `LibraryController`.

### Services Bibliothèque

`backend/services/library/library_service.py` orchestre les lectures publiques :

- `list_platforms(criteria)` ;
- `get_platform(platform_id)` ;
- `list_games(criteria)` ;
- `get_game(game_id)`.

`LibraryService.get_platform` ouvre une connexion, lit la plateforme via
`SqlAlchemyPlatformRepository.find_public_library_platform`, puis sérialise via
`LibraryPayloadSerializer.platform_payload`.

### Repository Plateformes

`backend/services/database/platform_repository.py` lit `t_platform` et
`t_platform_alias`. Les plateformes sont mises en cache via
`PlatformCatalogCache` pendant cinq heures.

Point d'attention : ne pas mélanger les images acceptées dans le cache existant
des plateformes, sinon une validation admin pourrait rester invisible jusqu'à
expiration ou invalidation du cache. Deux options sûres :

- charger les images acceptées séparément dans `LibraryService.get_platform`
  après la lecture de la plateforme ;
- ou invalider explicitement `PlatformCatalogCache` à chaque modération, ce qui
  est plus large que nécessaire.

La première option est recommandée.

### Pagination

La pagination publique Bibliothèque repose sur :

- `LibraryQueryParser` dans `backend/services/library/library_query_contract.py` ;
- `LibraryQueryCriteria` ;
- `LibraryPayloadSerializer.page_payload`.

La liste admin des images doit réutiliser le même format de réponse `page` :

```json
{
  "page": {
    "page": 0,
    "size": 500,
    "totalElements": 1,
    "totalPages": 1
  }
}
```

Le parseur existant accepte déjà `page`, `size` et `sort`, mais ses colonnes
autorisées sont dédiées à `platforms`, `studios` et `games`. Il faudra soit
l'étendre avec une entité logique `platform_images`, soit créer un parseur dédié
réutilisant `LibraryPageRequest`.

### Authentification

`backend/services/auth/auth_guard.py` fournit :

- `protect_all_routes` ;
- `require_profile(UserProfile.ADMIN.value)` ;
- `get_current_token_payload()`.

Les endpoints d'upload devront utiliser le profil minimal `USER`, qui inclut
`ADMIN` côté backend par hiérarchie. L'utilisateur proposant l'image doit être
dérivé du token validé, via `sub`, sans champ utilisateur dans le payload.
Cette valeur doit être persistée dans `t_platform_image.user_id` à l'insertion.

Les endpoints de modération doivent utiliser `require_profile("ADMIN")`.

### Email

Le projet dispose déjà de :

- `backend/services/email/email_configuration.py` ;
- `backend/services/email/email_sender.py` ;
- `EmailSenderFactory` ;
- `ADMIN_NOTIFICATION_EMAIL`, déjà utilisé par les notifications admin.

Le pattern le plus proche est
`backend/services/database/platform_matching_admin_notifier.py`.

Pour les images, créer un notifier dédié est recommandé, par exemple :

- `backend/services/library/platform_image_admin_notifier.py`.

Il devra :

- lire `ADMIN_NOTIFICATION_EMAIL` par défaut ;
- ne pas envoyer d'email si la variable est vide ;
- journaliser un warning si aucune adresse admin n'est configurée, comme demandé
  par la tâche ;
- utiliser `EmailConfiguration.from_environment()` et `EmailSenderFactory`.

### Configuration Et Stockage Disque

Le pattern de configuration le plus proche est
`backend/services/users/user_collection_import_configuration.py`.

Créer une configuration dédiée est recommandé :

- `backend/services/library/platform_image_configuration.py`.

Contrat cible :

- `BACKEND_IMG_DIR`, défaut recommandé : `/images` ;
- `PLATFORM_IMAGE_MAX_UPLOAD_BYTES`, défaut recommandé : `10485760` ;
- création du répertoire si nécessaire ;
- validation d'entier strictement positif.

Le stockage cible est :

```text
{BACKEND_IMG_DIR}/platforms/{slug nom}/{nom_original}
```

En cas de collision, ajouter un suffixe compteur avant l'extension :

```text
image.png
image-1.png
image-2.png
```

Le slug recommandé : minuscules, accents retirés, caractères non
alphanumériques remplacés par `-`, tirets multiples compressés, fallback
`platform-{id}` si vide.

### Schéma SQL Existant

Les modèles ORM sont sous `backend/services/database/`, un fichier par classe.
Les modèles concernés :

- `platform.py` pour `t_platform` ;
- `user.py` pour `t_user`.

Les migrations actuelles vont jusqu'à `20260614_0008`.

La nouvelle migration doit être une nouvelle révision, par exemple :

```text
backend/migrations/versions/20260618_0009_add_platform_images.py
```

Ne pas modifier les migrations existantes.

## Cartographie Frontend

### Détail Plateforme

La page publique est :

- `frontend/src/components/LibraryPlatformDetailView.jsx`.

Le hook de chargement est :

- `frontend/src/hooks/library/useLibraryPlatformDetailPage.js`.

Le service HTTP public est :

- `frontend/src/services/LibraryApi.js`.

La page est actuellement publique, via `/bibliotheque/plateformes/<platform_id>`.
Elle n'a pas d'état d'upload ni d'affichage image.

### Configuration Admin

La page Configuration est :

- `frontend/src/components/ConfigurationView.jsx`.

Elle reçoit ses permissions et callbacks depuis :

- `frontend/src/hooks/app/useCloudCollectionViewModel.js`.

Les actions admin existantes utilisent :

- `frontend/src/services/LibraryAdminApi.js` ;
- `frontend/src/hooks/library/useLibraryResetAction.js` ;
- `frontend/src/hooks/library/usePlatformCatalogSyncAction.js`.

Le pattern recommandé est de créer :

- `frontend/src/hooks/library/usePlatformImageModeration.js` ;
- éventuellement `frontend/src/components/PlatformImageModerationSection.jsx`.

`ConfigurationView.jsx` doit rester une page de composition et ne pas porter la
logique de pagination, filtres, appels API et modales.

### Permissions Frontend

`frontend/src/services/BackendRouteAccessService.js` calcule les flags
d'action depuis `/api/routes`.

Ajouter un flag dédié est recommandé :

```js
canModeratePlatformImages
```

Il doit vérifier :

```text
GET /api/library/platforms/images
```

Les actions de modification peuvent être appelées depuis la section uniquement
si la liste admin est autorisée. Les droits restent de toute façon imposés par
le backend.

### Tableau Et Pagination

Le tableau commun est :

- `frontend/src/components/TableComponent.jsx`.

Il supporte :

- `rows` ;
- `columns` ;
- `columnLabels` ;
- `pagination` ;
- `renderRowActions` ;
- `renderColumnFilter`.

`frontend/src/hooks/library/useLibraryEntityList.js` donne un bon modèle de
pagination frontend, mais il est orienté listes publiques avec filtre `name`.
Pour les images, un hook dédié est plus clair afin de gérer `status`,
`platform`, actions et rafraîchissement après modération.

## Architecture Cible Proposée

### Backend - Nouveaux Fichiers

Créer :

- `backend/controllers/platform_image_controller.py`
- `backend/services/library/platform_image_configuration.py`
- `backend/services/library/platform_image_service.py`
- `backend/services/library/platform_image_admin_notifier.py`
- `backend/services/database/platform_image.py`
- `backend/services/database/platform_image_repository.py`
- `backend/migrations/versions/20260618_0009_add_platform_images.py`

Exporter les nouveaux objets si nécessaire dans :

- `backend/controllers/__init__.py`
- `backend/services/__init__.py`
- `backend/services/database/__init__.py`
- `backend/services/library/__init__.py`

Modifier :

- `backend/app.py`, pour instancier et enregistrer `PlatformImageController` ;
- `backend/controllers/platform_controller.py`, seulement si le détail
  plateforme reste enrichi par `LibraryService` ;
- `backend/services/library/library_service.py`, pour enrichir le détail
  plateforme avec les images acceptées ;
- `backend/services/library/library_payload_serializer.py`, pour sérialiser
  `images`.

### Backend - Responsabilités

`PlatformImageController` :

- enregistre les routes ;
- applique `require_profile` sur les routes protégées ;
- expose le endpoint public image dans `get_public_endpoint_names()` ;
- lit `request.files["image"]` ;
- mappe les exceptions métier vers les statuts HTTP ;
- retourne les fichiers avec `send_file`.

`PlatformImageService` :

- valide plateforme, taille, extension et MIME ;
- construit le slug ;
- choisit le nom disque final ;
- copie le fichier ;
- orchestre l'insertion SQL ;
- envoie la notification admin ;
- accepte/refuse une image ;
- définit une image `MAIN`.

`SqlAlchemyPlatformImageRepository` :

- insère une image ;
- liste les images paginées pour admin ;
- compte les images filtrées ;
- retrouve une image par plateforme et id ;
- liste les images `ACCEPTED` d'une plateforme ;
- passe une image en `ACCEPTED` ;
- supprime une image ;
- bascule les autres images de la plateforme en `OTHER` ;
- passe une image en `MAIN`.

### Backend - Endpoints Cibles

Endpoints publics :

```http
GET /api/library/platforms/{platform_id}/image/{image_id}
```

Endpoints protégés `USER` :

```http
POST /api/library/platforms/{platform_id}/image
```

Endpoints protégés `ADMIN` :

```http
GET /api/library/platforms/images
PUT /api/library/platforms/{platform_id}/image/{image_id}/type/{type}
PUT /api/library/platforms/{platform_id}/image/{image_id}/status/{status}
```

### Backend - Payloads Recommandés

`POST /api/library/platforms/{id}/image`, en succès `201` :

```json
{
  "image": {
    "id": 12,
    "platform_id": 3,
    "type": "OTHER",
    "status": "WAITING_VALIDATION"
  }
}
```

`GET /api/library/platforms/{id}`, détail plateforme enrichi :

```json
{
  "platform": {
    "id": 3,
    "name": "Super NES",
    "images": [
      {
        "id": 12,
        "type": "MAIN"
      }
    ]
  }
}
```

La tâche indique que le lien peut être reconstruit depuis `platform.id`,
`image.id` et `type`. Il n'est donc pas nécessaire de renvoyer `url`. Le
cache-busting peut être reconstruit côté frontend en ajoutant une query string
stable basée sur une version. Si aucune version n'est renvoyée, utiliser
`image.id` suffit pour les nouvelles images, mais pas pour un changement de
fichier à identifiant constant. Comme le fichier ne change pas après création,
`?v={image.id}` est acceptable.

`GET /api/library/platforms/images`, réponse admin :

```json
{
  "images": [
    {
      "id": 12,
      "platform_id": 3,
      "platform_name": "Super NES",
      "type": "OTHER",
      "status": "WAITING_VALIDATION",
      "user_id": 7,
      "user_email": "user@example.com",
      "creation_date": "2026-06-18T10:30:00"
    }
  ],
  "page": {
    "page": 0,
    "size": 500,
    "totalElements": 1,
    "totalPages": 1
  }
}
```

### Base De Données

Table cible `t_platform_image` :

| Colonne | Type recommandé | Null | Notes |
| --- | --- | --- | --- |
| `id` | `BIGINT` | Non | Séquence `s_platform_image` |
| `platform` | `BIGINT` | Non | FK vers `t_platform.id` |
| `path` | `VARCHAR(1024)` | Non | Chemin absolu |
| `type` | `VARCHAR(16)` | Non | `MAIN`, `OTHER` |
| `status` | `VARCHAR(32)` | Non | `WAITING_VALIDATION`, `ACCEPTED` |
| `user_id` | `BIGINT` | Non | FK vers `t_user.id` |
| `creation_date` | `TIMESTAMP` | Non | Date de proposition |

Contraintes recommandées :

- primary key `id` ;
- foreign key `platform -> t_platform.id` ;
- foreign key `user_id -> t_user.id` ;
- check `type in ('MAIN', 'OTHER')` ;
- check `status in ('WAITING_VALIDATION', 'ACCEPTED')` ;
- index `ix_t_platform_image_platform` ;
- index `ix_t_platform_image_status` ;
- index `ix_t_platform_image_user_id` ;
- unique partiel PostgreSQL sur `platform` quand `type = 'MAIN'`.

Nom recommandé de la contrainte unique partielle :

```text
uq_t_platform_image_single_main
```

### Frontend - Nouveaux Fichiers

Créer :

- `frontend/src/services/PlatformImageApi.js` ou étendre `LibraryAdminApi.js`
  pour les routes admin et protégées ;
- `frontend/src/hooks/library/usePlatformImageUpload.js` ou intégrer l'upload
  dans `useLibraryPlatformDetailPage` si le hook reste sous 150 lignes ;
- `frontend/src/hooks/library/usePlatformImageModeration.js` ;
- `frontend/src/components/PlatformImageGallery.jsx` ;
- `frontend/src/components/PlatformImageUploadControl.jsx` ;
- `frontend/src/components/PlatformImageModerationSection.jsx`.

Modifier :

- `frontend/src/hooks/library/useLibraryPlatformDetailPage.js` ;
- `frontend/src/components/LibraryPlatformDetailView.jsx` ;
- `frontend/src/components/ConfigurationView.jsx` ;
- `frontend/src/hooks/app/useCloudCollectionViewModel.js` ;
- `frontend/src/services/BackendRouteAccessService.js` ;
- `frontend/src/services/LibraryApi.js`, pour construire les URLs d'images
  publiques.

### Frontend - Règles UI Cibles

Page détail plateforme :

- reste publique ;
- bouton upload visible seulement si `isAuthenticated` ;
- upload via `FormData` avec champ `image` ;
- erreurs affichées via message local ;
- image `MAIN` mise en avant ;
- fallback vers la première `OTHER` si aucune `MAIN` ;
- diaporama limité à 5 autres images ;
- aucun bloc image si aucune image.

Configuration :

- section visible uniquement pour `ADMIN` et permission route catalog ;
- filtres `status` et `platform` via `<select>` ;
- pagination via `TableComponent` ;
- miniature redimensionnée côté frontend ;
- clic miniature ouvrant une vue agrandie ;
- actions accepter, refuser, définir `MAIN`.

## Décisions De Contrat

- Le endpoint public d'image doit être explicitement ajouté aux exceptions
  publiques dans `authentication.md`.
- L'upload est protégé `USER`, donc un `ADMIN` est aussi accepté côté backend
  par hiérarchie. Côté frontend, le bouton peut être visible pour tout utilisateur
  connecté, y compris `ADMIN`, sauf décision contraire ultérieure.
- La modération est réservée `ADMIN`.
- Le refus ne crée pas de statut `REFUSED` en base ; il supprime fichier et ligne.
- `user_id` est obligatoire et doit toujours correspondre à l'utilisateur
  connecté à l'origine de l'upload ; le frontend ne fournit jamais cette valeur.
- Le détail plateforme ne doit exposer que les images `ACCEPTED`.
- Le chemin disque absolu est stocké comme demandé, même si un chemin relatif
  serait plus portable.
- Les images publiques ne nécessitent pas de Bearer token.
- Le MIME et l'extension doivent être validés. Les couples recommandés :
  - `.jpg`, `.jpeg` avec `image/jpeg` ;
  - `.png` avec `image/png` ;
  - `.webp` avec `image/webp` ;
  - `.gif` avec `image/gif`.

## Risques Identifiés

- Le cache plateforme existant peut masquer les images acceptées si elles sont
  ajoutées directement aux lignes cachées.
- `app.config["MAX_CONTENT_LENGTH"]` utilise actuellement la limite d'import de
  collection. Pour une limite image plus basse, il faudra valider la taille dans
  le service plutôt que remplacer globalement `MAX_CONTENT_LENGTH`, ou prendre
  la valeur maximale globale et contrôler par domaine.
- Une contrainte unique partielle est spécifique PostgreSQL. C'est cohérent avec
  `documentation/database.md`, qui désigne PostgreSQL comme moteur cible.
- Les images publiques exposent des fichiers disque. Le service doit vérifier
  que le chemin retourné est bien issu de `BACKEND_IMG_DIR` et que l'image est
  `ACCEPTED`.
- Les noms originaux de fichiers doivent être nettoyés avec `secure_filename`
  ou une logique équivalente pour éviter les chemins relatifs ou caractères
  dangereux.
- L'écran Configuration risque de dépasser les limites de lisibilité si toute la
  modération est ajoutée directement dans `ConfigurationView.jsx`; extraire des
  composants dédiés.

## Tests À Prévoir

### Backend

Créer ou modifier :

- `backend/tests/test_platform_image_configuration.py`
- `backend/tests/test_platform_image_repository.py`
- `backend/tests/test_platform_image_service.py`
- `backend/tests/test_platform_image_routes.py`
- `backend/tests/test_library_routes.py`
- `backend/tests/test_library_service.py`
- `backend/tests/test_database_schema_service.py`
- `backend/tests/test_library_reset_routes.py` ou un test route catalog dédié
  pour vérifier les métadonnées des nouveaux endpoints.

Couvertures minimales :

- config env valide/invalide ;
- création du répertoire d'images ;
- extension et MIME acceptés/refusés ;
- limite `PLATFORM_IMAGE_MAX_UPLOAD_BYTES` ;
- création `WAITING_VALIDATION`/`OTHER` ;
- insertion avec `user_id` dérivé du token ;
- collision de nom fichier ;
- plateforme inconnue ;
- refus sans token ;
- refus `USER` sur endpoints admin ;
- accès `ADMIN` aux endpoints admin ;
- image `WAITING_VALIDATION` non servie publiquement ;
- image `ACCEPTED` servie publiquement ;
- détail plateforme enrichi avec images acceptées ;
- acceptation ;
- refus avec suppression SQL et disque ;
- définition `MAIN` avec bascule des autres images en `OTHER` ;
- route catalog.

### Frontend

Le projet ne montre pas de suite de tests frontend dédiée dans l'analyse. La
validation minimale sera :

- `npm run build` depuis `frontend/` ;
- vérification manuelle ou locale des états principaux si un serveur est lancé.

Si des tests frontend sont ajoutés ultérieurement, couvrir :

- bouton upload visible connecté et absent anonyme ;
- galerie sans image, avec `MAIN`, avec seulement `OTHER` ;
- section admin visible uniquement `ADMIN` ;
- filtres/pagination ;
- actions accepter/refuser/MAIN.

## Validations À Exécuter En Fin De Chantier

- `./test_backend.sh`
- `npm run build` dans `frontend/`
- rebuild Docker backend et web, car le runtime et les volumes changent
- vérification des fichiers Docker Compose local et online
- vérification README et documentation

Le navigateur intégré `iab` est documenté comme indisponible dans ce workspace ;
ne pas le prévoir comme validation obligatoire.

## Documentation À Mettre À Jour

Obligatoire :

- `documentation/backend-api.md`
- `documentation/authentication.md`
- `documentation/database.md`
- `documentation/site-plan.md`
- `documentation/frontend-arch.md`
- `documentation/backend-arch.md`
- `README.md`

À vérifier :

- `documentation/menu.md`, probablement non concerné si aucune entrée de menu
  n'est ajoutée.

## Écarts Et Points D'Attention

- La tâche mentionne une liste de "toutes les entrées de la table
  `t_paltformes_images`", mais le nom contractuel corrigé est `t_platform_image`.
- La tâche indique que le détail plateforme retourne seulement `id` et `type`
  des images. Pour une UI admin, la liste admin doit retourner davantage de
  champs, mais cela concerne `GET /api/library/platforms/images`, pas le détail
  public.
- Le cache-busting est demandé, mais aucun champ de version n'est demandé dans
  le payload public. L'usage de `?v={image.id}` est suffisant tant que le fichier
  d'une ligne n'est jamais remplacé.
- Les modifications documentaires changent une règle existante :
  `documentation/authentication.md` devra ajouter une nouvelle route publique.
  Cette exception est explicitement demandée par la tâche, mais doit être
  documentée et testée.

## Ordre D'Implémentation Recommandé

1. Schéma SQL, modèle, configuration et Docker.
2. Repository et service backend images.
3. Upload utilisateur et lecture publique des images acceptées.
4. Endpoints admin de modération.
5. Détail plateforme frontend et upload.
6. Section admin frontend.
7. Documentation.
8. Validation finale et rebuild Docker.
