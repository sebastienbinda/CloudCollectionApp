# 00 - Rapport d'analyse du code existant

## Synthèse

Le workflow d'import utilisateur est actuellement fonctionnel, transactionnel et
centré sur un fichier ODS à structure fixe. Le frontend envoie uniquement
`collection_file` dans un `multipart/form-data`. Le backend copie le fichier,
lit l'ODS via `OdsCollectionImportReader`, persiste les plateformes, studios,
jeux et associations SQL, puis renseigne `t_user.collection_file_path`.

La table `t_user` contient déjà `collection_file_description` en `JSONB`, mais
le workflow actuel ne lit, ne valide et ne sauvegarde aucune description
d'import. L'import est encore fortement couplé aux classes ODS jusque dans
`UserCollectionImportService`, `SqlAlchemyUserCollectionImportRepository` et
`SqlAlchemyGameRepository`.

L'architecture cible doit introduire un contrat générique de fichier de
collection avant de rendre le reader ODS configurable. Le service d'import
utilisateur doit dépendre d'une abstraction de reader et d'un modèle métier
générique, pas d'un modèle ODS.

## Documentations Relues

- `documentation/import.md` : workflow import actuel, statut collection,
  règles ODS fixes et validations attendues.
- `documentation/backend-api.md` : contrat actuel de
  `GET /api/users/me/collection` et `POST /api/users/import`.
- `documentation/backend-arch.md` : contrôleurs HTTP sous `backend/controllers/`,
  workflows métier sous `backend/services/`, repositories SQL sous
  `backend/services/database/`, parsing ODS sous `backend/services/ods/`.
- `documentation/frontend-arch.md` : orchestration frontend dans
  `frontend/src/hooks/collection/`, appels HTTP dans `frontend/src/services/`.
- `documentation/database.md` : `t_user.collection_file_description` existe
  déjà en `JSONB`.
- `documentation/site-plan.md` : `/collection/import` reste la page onboarding
  pour les utilisateurs non `ADMIN` sans collection.
- `tasks/import_configuration/import_configuration.md` : tâche chapeau et
  contrat cible.

## Cartographie Backend Actuelle

### Controller

`backend/controllers/user_collection_import_controller.py`

- Enregistre :
  - `GET /api/users/me/collection`
  - `POST /api/users/import`
- Récupère l'utilisateur connecté via `AuthGuard`.
- Lit uniquement `request.files["collection_file"]`.
- Sauvegarde l'upload dans un fichier temporaire suffixé `.ods`.
- Instancie `UserCollectionImportService` avec :
  - `UserCollectionImportConfiguration.from_environment()`
  - `SqlAlchemyUserCollectionImportRepository`
  - `OdsCollectionImportReader`
- Mappe les erreurs métier actuelles :
  - `UserCollectionImportInvalidFileError` -> `400`
  - `UserCollectionImportTooLargeError` -> `413`
  - `UserCollectionImportConflictError` -> `409`
  - `UserCollectionImportUnexpectedError` -> `500`

Le controller devra seulement décoder le champ texte multipart
`collection_file_description`, déléguer sa validation à un service/DTO, et
mapper la nouvelle erreur de configuration en `422`.

### Service Métier

`backend/services/users/user_collection_import_service.py`

- Orchestre l'import complet.
- Applique un verrou applicatif par utilisateur.
- Vérifie qu'aucune collection n'existe déjà.
- Vérifie actuellement l'extension `.ods` et la taille maximale.
- Copie le fichier dans `/users/workspace/<user_id>/<user_id>-collection.ods`.
- Appelle `self.ods_reader.read(str(copied_file_path))`.
- Appelle `repository.import_collection(user_id, path, import_data)`.
- Supprime le fichier copié en cas d'échec.

Couplages ODS à supprimer :

- import de `OdsCollectionImportData`;
- import de `OdsCollectionImportReadError`;
- import de `OdsCollectionImportReader`;
- import de `OdsCollectionImportValidationError`;
- attribut `self.ods_reader`;
- validation d'extension fixée à `.ods` dans le service métier ;
- chemin final toujours suffixé `-collection.ods`.

Dans l'architecture cible, la connaissance des extensions acceptées ne doit pas
rester dans `UserCollectionImportService`. Elle doit être portée par le reader
spécifique instancié via `file_type`, ou par une metadata de format retournée
avec ce reader par la factory.

### Reader ODS

`backend/services/ods/ods_collection_import_reader.py`

- Lit une structure ODS fixe.
- Liste les onglets via `OdsReader.list_platforms()`.
- Ignore `Accueil` et `Liste de souhaits`.
- Interprète toujours le nom de l'onglet comme plateforme.
- Lit les jeux via `OdsReader.read_games_dataframe(sheet_name)`.
- Exige les colonnes françaises :
  - `Nom du jeu`
  - `Studio`
  - `Date de sortie`
- Transforme vers :
  - `OdsCollectionImportPlatform`
  - `OdsCollectionImportStudio`
  - `OdsCollectionImportGame`
  - `OdsCollectionImportData`

`backend/services/ods/ods_reader.py`

- Lit tous les onglets sauf `Accueil` et `Liste de souhaits`.
- Lit chaque feuille avec :
  - `engine="odf"`
  - `header=5`
  - `usecols="F:M"`
- Fait un fallback XML via `OdsXmlReader`.

Ces valeurs fixes (`header=5`, `usecols="F:M"`, exclusions d'onglets et noms de
colonnes français) sont le coeur de l'ancien mode à supprimer.

### DTOs Existants

`backend/services/ods/ods_collection_import_models.py`

- `OdsCollectionImportPlatform`
- `OdsCollectionImportStudio`
- `OdsCollectionImportGame`
- `OdsCollectionImportData`

Ces DTOs portent des noms ODS mais leur contenu est déjà assez générique pour
l'import SQL actuel. La suite doit les renommer ou les encapsuler sous un nom
agnostique, par exemple :

- `CollectionImportPlatform`
- `CollectionImportStudio`
- `CollectionImportGame`
- `CollectionImportData`

### Repositories SQL

`backend/services/database/user_collection_import_repository.py`

- Orchestre la transaction SQL d'import.
- Reçoit actuellement `OdsCollectionImportData`.
- Appelle :
  - `SqlAlchemyUserCollectionFileRepository`
  - `SqlAlchemyPlatformRepository`
  - `SqlAlchemyStudioRepository`
  - `SqlAlchemyGameRepository`
  - `SqlAlchemyUserCollectionRepository`
- Renseigne actuellement uniquement `collection_file_path`.

`backend/services/database/user_collection_file_repository.py`

- Lit `collection_file_path` pour déterminer si une collection existe.
- Verrouille `t_user` avec `FOR UPDATE`.
- Met à jour seulement `collection_file_path`.
- Ne met pas encore à jour `collection_file_description`.

`backend/services/database/game_repository.py`

- Dépend directement de `OdsCollectionImportGame`.
- Utilise `game.name`, `game.release_date`, `game.platform_name`,
  `game.studio_name`.

`backend/services/database/platform_repository.py`
et `backend/services/database/studio_repository.py`

- Ne dépendent pas directement d'ODS.
- Peuvent être conservés tels quels.

`backend/services/database/user_collection_repository.py`

- Crée les associations `t_user_collection`.
- Ne dépend pas d'ODS.

### Schéma Base

`documentation/database.md` et le modèle `backend/services/database/user.py`
déclarent déjà :

- `t_user.collection_file_path VARCHAR(512)`
- `t_user.collection_file_description JSONB`

Aucune migration n'est attendue si les migrations locales et l'environnement
cible contiennent bien cette colonne. La tâche `03` devra tout de même vérifier
que le repository sait la persister.

## Cartographie Frontend Actuelle

### Page Onboarding

`frontend/src/components/UserCollectionOnboardingView.jsx`

- Affiche trois étapes simples : sélectionner, importer, consulter.
- Propose seulement un input fichier :
  - `accept=".ods"`
- Ne collecte aucune configuration.
- Appelle `onFileChange` et `onSubmitImport`.

Cette page devra collecter les trois modes de configuration :

- fichier à feuille unique ;
- plusieurs feuilles avec layout partagé ;
- plusieurs feuilles avec layout par feuille.

### Hook

`frontend/src/hooks/collection/useUserCollectionOnboarding.js`

- Vérifie le statut via `UserCollectionApi.fetchCurrentCollectionStatus()`.
- Stocke seulement `selectedCollectionFile`.
- Appelle `UserCollectionApi.importCollection(selectedCollectionFile)`.
- Affiche des messages par code d'erreur.

Le hook devra stocker l'état du formulaire de configuration, construire le JSON
ou déléguer cette construction à une fonction pure, puis transmettre le fichier
et la description au service API.

### Service HTTP

`frontend/src/services/UserCollectionApi.js`

- Crée un `FormData`.
- Ajoute uniquement :
  - `collection_file`
- N'ajoute pas manuellement le `Content-Type`, ce qui est correct.

Le service devra ajouter :

```javascript
formData.append("collection_file_description", JSON.stringify(description));
```

Il devra aussi normaliser les erreurs `422`, en conservant `details` pour
l'affichage.

### Tests Frontend

Le dépôt ne montre pas de suite de tests frontend dédiée à ce workflow. La
validation frontend attendue reste donc au minimum `npm run build`, avec des
tests unitaires à ajouter uniquement si le projet introduit une structure de
tests frontend.

## Architecture Cible Proposée

### Nouveau Domaine Technique

Créer un sous-domaine agnostique, idéalement sous :

```text
backend/services/collection/imports/
```

ou, si l'équipe préfère garder l'import utilisateur sous `users/` :

```text
backend/services/users/imports/
```

Recommandation : `backend/services/collection/imports/`, car les objets
représentent le fichier de collection et non la gestion utilisateur.

### DTOs Et Enums

Créer des objets génériques :

- `CollectionFileType`
  - `LIBREOFFICE_ODS = "libreoffice_ods"`
- `CollectionImportField`
  - `NAME = "name"`
  - `PLATFORM = "platform"`
  - `STUDIO = "studio"`
  - `RELEASE_DATE = "release_date"`
- `CollectionFileDescription`
  - `file_type`
  - `single_sheet_conf`
  - `multiple_sheets_conf`
- `CollectionSheetLayout`
  - `data_range`
  - `header_row`
  - `column_information`
- `CollectionImportData`
- `CollectionImportPlatform`
- `CollectionImportStudio`
- `CollectionImportGame`

Le modèle de sortie doit remplacer progressivement les classes
`OdsCollectionImport*` dans le service et les repositories SQL.

### Validation De Configuration

Créer un validateur dédié, par exemple :

```text
backend/services/collection/imports/collection_file_description_validator.py
```

Responsabilités :

- parser le JSON déjà décodé en dictionnaire ;
- construire `CollectionFileDescription` ;
- valider les modes exclusifs ;
- valider `file_type` ;
- valider `sheet_information` ;
- valider `data_range`, `header_row`, colonnes ;
- valider les champs obligatoires ;
- retourner toutes les erreurs de configuration sous forme de liste.

Créer une exception dédiée :

```text
CollectionFileDescriptionValidationError
```

Elle doit contenir `details: list[str]` et être mappée en `422` par le
controller.

La validation de présence réelle des onglets (`included_sheets`) doit être
réalisée par le reader du format concerné, car elle dépend du fichier. Elle doit
remonter comme erreur de configuration `422`, pas comme fichier invalide `400`,
lorsque la configuration référence un onglet absent.

### Interface Reader

Créer un protocole :

```python
class CollectionFileReader(Protocol):
    @property
    def accepted_extensions(self) -> tuple[str, ...]:
        ...

    def read(
        self,
        file_path: str,
        description: CollectionFileDescription,
    ) -> CollectionImportData:
        ...
```

Créer une factory :

```python
class CollectionFileReaderFactory:
    def create(self, file_type: CollectionFileType) -> CollectionFileReader:
        ...
```

La factory est le seul endroit générique qui connaît le mapping :

- `libreoffice_ods` -> reader ODS configurable.

Le reader ou l'objet retourné par la factory doit aussi exposer les contraintes
propres au format, notamment les extensions autorisées. Par exemple le reader
`libreoffice_ods` expose `.ods`, tandis qu'un futur reader `excel_xlsx`
exposera `.xlsx`. Le service métier peut appliquer ces contraintes sans
hardcoder les extensions.

Pour tester la généricité, utiliser un faux reader ASCII ou un fake reader via
la factory sans modifier `UserCollectionImportService`.

### Implémentation ODS

Adapter l'existant en conservant la responsabilité ODS sous
`backend/services/ods/`.

Option recommandée :

- garder `OdsReader` comme lecteur bas niveau ODS ;
- créer ou renommer `OdsCollectionImportReader` pour qu'il implémente
  `CollectionFileReader`;
- supprimer l'interprétation fixe :
  - plus de `EXCLUDED_SHEET_NAMES`;
  - plus de `REQUIRED_GAME_COLUMNS` en noms français fixes ;
  - plus de `header=5`;
  - plus de `usecols="F:M"`;
  - plus de plateforme forcément issue du nom d'onglet.

Le reader ODS configurable devra :

- lire les feuilles demandées ;
- appliquer `data_range`, `header_row` et `column_information` ;
- injecter la valeur portée par l'onglet lorsque `sheet_information` est défini ;
- produire `CollectionImportData`.

### Service D'Import Utilisateur

Modifier `UserCollectionImportService` pour recevoir :

- `configuration: UserCollectionImportConfiguration`
- `repository: UserCollectionImportRepository`
- `reader_factory: CollectionFileReaderFactory`

Modifier la signature métier :

```python
def import_collection(
    self,
    user_id: int,
    source_file_path: str,
    original_filename: str | None,
    file_description: CollectionFileDescription,
) -> UserCollectionImportResult:
```

Responsabilités du service :

- vérifier l'absence de collection ;
- demander le reader à la factory ;
- vérifier la taille maximale applicative ;
- vérifier l'extension à partir des extensions exposées par le reader retourné
  par la factory, sans connaître directement `.ods` ou `.xlsx` ;
- copier le fichier avec l'extension du fichier source validée par le reader ;
- appeler `reader.read(copied_file_path, file_description)`;
- persister les données importées et la description validée.

### Repository Transactionnel

Modifier `UserCollectionImportRepository.import_collection` pour recevoir :

- `import_data: CollectionImportData`
- `collection_file_description: dict`

Modifier `SqlAlchemyUserCollectionFileRepository` :

- ajouter une méthode qui met à jour en même temps :
  - `collection_file_path`
  - `collection_file_description`

Cette mise à jour doit rester dans la même transaction que les insertions SQL.

### Controller

Modifier `UserCollectionImportController.import_current_user_collection` :

- lire `request.form.get("collection_file_description")`;
- retourner `422` si absent ou JSON invalide ;
- déléguer la construction/validation du DTO au validateur ou service dédié ;
- transmettre le DTO validé au service d'import ;
- mapper `CollectionFileDescriptionValidationError` en :

```json
{
  "error": "Configuration invalide.",
  "details": [...]
}
```

Le controller ne doit pas valider lui-même les règles métier de configuration.

## Tests À Prévoir

### Backend Route

Modifier `backend/tests/test_user_collection_routes.py` :

- succès avec `collection_file` et `collection_file_description` ;
- absence de `collection_file_description` -> `422` ;
- JSON invalide -> `422` ;
- erreur de validation de configuration -> `422` avec `details` ;
- les mappings `400`, `409`, `413`, `500` restent inchangés.

### Validation De Configuration

Créer un test dédié, par exemple :

```text
backend/tests/test_collection_file_description.py
```

Cas à couvrir :

- configuration `single_sheet_conf` valide ;
- configuration `multiple_sheets_conf.shared_layout` valide ;
- configuration `multiple_sheets_conf.sheets` valide ;
- `file_type` inconnu -> erreur ;
- conflit entre modes -> erreur ;
- aucun mode -> erreur ;
- champ obligatoire manquant -> erreur ;
- colonne hors `data_range` -> erreur ;
- `header_row` hors `data_range` -> erreur ;
- `sheet_information` inconnu -> erreur ;
- information portée par l'onglet aussi présente en colonne -> erreur ;
- `sheets[].sheet_name` absent ou vide -> erreur.

### Reader Générique Et Factory

Créer ou modifier des tests pour valider :

- `CollectionFileReaderFactory` retourne le reader ODS pour `libreoffice_ods` ;
- `UserCollectionImportService` peut utiliser un fake reader non ODS sans
  modification ;
- `file_type` inconnu ne sélectionne aucun reader.

### Reader ODS Configurable

Modifier `backend/tests/test_ods_collection_import_reader.py` :

- import `single_sheet_conf` valide ;
- import `shared_layout` valide ;
- import `sheets` valide ;
- nom d'onglet injecté dans `platform` ;
- nom d'onglet injecté dans `studio` ;
- `included_sheets` avec onglet absent -> erreur de configuration ;
- date de sortie invalide -> `None` avec warning ;
- doublons plateformes, studios et jeux toujours dédupliqués.

### Repository Et Service

Modifier :

- `backend/tests/test_user_collection_import_service.py`
- tests repository existants ou nouveau test ciblé

Cas à couvrir :

- `collection_file_description` est sauvegardé uniquement après succès ;
- pas de sauvegarde si le reader échoue ;
- pas de sauvegarde si la persistance échoue ;
- chemin final cohérent avec l'extension validée par le reader ;
- conservation des comportements existants : conflit, taille, fichier invalide,
  nettoyage fichier.

### Frontend

Si des tests frontend sont ajoutés :

- construction JSON `single_sheet_conf` ;
- construction JSON `multiple_sheets_conf.shared_layout` ;
- construction JSON `multiple_sheets_conf.sheets` ;
- envoi `collection_file` et `collection_file_description` dans le même
  `FormData` ;
- affichage des erreurs `422.details`.

Validation minimale :

```bash
cd frontend
npm run build
```

## Risques Identifiés

- `OdsCollectionImportData` est utilisé au-delà du reader ODS, notamment dans le
  service et les repositories. Renommer ou remplacer ces DTOs doit être fait
  proprement pour éviter un changement trop large et fragile.
- La lecture `data_range` peut être interprétée différemment par pandas et par
  le fallback XML. Il faudra centraliser la conversion de plage tableur pour ne
  pas dupliquer la logique.
- `included_sheets` absent signifie importer tous les onglets. Cela peut
  importer des feuilles non souhaitées si l'utilisateur ne les exclut pas.
- Le champ `collection_file_description` existe dans le modèle et la
  documentation, mais il faut vérifier l'état réel des migrations déployées.
- Le service valide aujourd'hui seulement `.ods`. Avec `file_type`, la validation
  d'extension doit être fournie par le reader spécifique ou sa metadata de
  format, afin que le service reste agnostique et ne bloque pas `excel_xlsx`.
- Le frontend risque de grossir rapidement si les trois modes sont codés dans un
  seul composant. Il faudra extraire des helpers ou petits composants si
  `UserCollectionOnboardingView.jsx` approche la limite de 500 lignes.
- La compatibilité documentaire doit être revue : `documentation/import.md` et
  `documentation/backend-api.md` décrivent encore l'import ODS fixe.

## Écarts Avec La Tâche Chapeau

- La tâche chapeau indique qu'aucune migration n'est à prévoir. Le schéma
  documenté et le modèle ORM contiennent bien `collection_file_description`.
  L'analyse ne demande donc pas de migration, mais la tâche `03` devra confirmer
  que la migration versionnée correspond à ce contrat.
- La tâche chapeau indique que la notion d'onglet technique n'existe plus. Cela
  implique de supprimer l'exclusion automatique `Accueil` et `Liste de souhaits`
  dans le nouveau reader configurable, même si l'ancien import les ignorait.
- Le contrat cible demande une généricité future pour Excel. Pour y parvenir, il
  ne suffit pas d'adapter `OdsCollectionImportReader`; il faut aussi retirer les
  types ODS des repositories et du service d'import.

## Ordre D'Implémentation Recommandé

1. Créer les DTOs/enums/validateur `CollectionFileDescription`.
2. Adapter les tests route pour le champ multipart
   `collection_file_description`.
3. Introduire `CollectionFileReader`, `CollectionFileReaderFactory` et les DTOs
   de sortie génériques.
4. Adapter `UserCollectionImportService` à la factory et au DTO générique.
5. Adapter le repository transactionnel pour sauvegarder
   `collection_file_description`.
6. Rendre le reader ODS configurable.
7. Adapter le frontend onboarding et `UserCollectionApi`.
8. Mettre à jour la documentation et lancer les validations complètes.
