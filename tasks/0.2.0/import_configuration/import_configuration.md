# Import configurable de collection

## Objectif

Adapter l'import de fichier de collection pour ne plus dépendre d'une structure
ODS codée en dur. L'utilisateur décrit où lire les données à importer via une
configuration JSON envoyée avec le fichier dans `POST /api/users/import`.

La solution doit préparer l'arrivée d'autres formats de fichiers, par exemple
Excel, en introduisant une interface générique de lecture de fichier de
collection.

## Sous-tâches

Les tâches doivent être réalisées dans l'ordre suivant :

1. `00_existing_code_analysis_and_architecture.md`
2. `01_import_configuration_contract.md`
3. `02_backend_generic_reader_architecture.md`
4. `03_backend_import_endpoint_and_persistence.md`
5. `04_frontend_onboarding_configuration.md`
6. `05_documentation_and_validation.md`

Chaque fichier est conçu pour être suffisamment autonome. La tâche `00` doit
être réalisée en premier et produire un court rapport d'analyse dans le dossier
`tasks/import_configuration/`.

## Contraintes Fonctionnelles

- L'ancien mode d'import ODS à structure fixe est supprimé.
- `POST /api/users/import` reste en `multipart/form-data`.
- Le fichier est envoyé dans le champ `collection_file`.
- La configuration est envoyée dans le champ texte
  `collection_file_description`, sous forme de JSON UTF-8.
- La configuration sauvegardée en base est celle qui a permis un import réussi.
- `GET /api/users/me/collection` n'est pas modifié.
- Aucune migration n'est attendue si `t_user.collection_file_description`
  existe déjà dans le schéma courant.

## Contrat de Configuration

Champs importables au périmètre initial :

- `name`
- `platform`
- `studio`
- `release_date`

`file_type` vaut actuellement `libreoffice_ods`. Le code doit être extensible
pour accepter plus tard `excel_xlsx`.

Une configuration contient exactement un des modes suivants :

- `single_sheet_conf`
- `multiple_sheets_conf.shared_layout`
- `multiple_sheets_conf.sheets`

## Réponse 422

Les erreurs de validation de configuration retournent `422` avec le format :

```json
{
  "error": "Configuration invalide.",
  "details": ["file_type inconnu", "colonne obligatoire manquante: name"]
}
```

## Documentation

`documentation/import.md` doit être mise à jour pour documenter :

- le nouveau fonctionnement configurable ;
- le contrat multipart ;
- le schéma JSON ;
- l'interface générique de reader ;
- l'objectif de supporter plusieurs types de fichiers.
