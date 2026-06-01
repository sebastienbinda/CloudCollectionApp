# 01 - Contrat de configuration d'import

## Objectif

Créer le contrat backend de configuration d'import, avec validation stricte et
erreurs `422`, sans encore modifier le parsing réel du fichier.

Cette tâche dépend de :

- `00_existing_code_analysis_and_architecture.md`
- `00_existing_code_analysis_result.md`

## Contrat Multipart

`POST /api/users/import` reste un endpoint `multipart/form-data`.

Champs attendus :

- `collection_file` : fichier de collection uploadé ;
- `collection_file_description` : champ texte contenant un JSON UTF-8.

## Champs Importables

Créer un enum extensible pour les champs importables :

- `name`
- `platform`
- `studio`
- `release_date`

Les champs requis au périmètre initial sont ces quatre champs.

## Types De Fichiers

Créer un enum extensible pour les types de fichiers :

- `libreoffice_ods`

Le code doit être prévu pour ajouter plus tard :

- `excel_xlsx`

## Modes De Configuration

Une configuration contient exactement un seul des modes suivants :

- `single_sheet_conf`
- `multiple_sheets_conf.shared_layout`
- `multiple_sheets_conf.sheets`

### Exemple Single Sheet

```json
{
  "file_type": "libreoffice_ods",
  "single_sheet_conf": {
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

### Exemple Multiple Sheets Avec Layout Partagé

```json
{
  "file_type": "libreoffice_ods",
  "multiple_sheets_conf": {
    "sheet_information": "platform",
    "shared_layout": {
      "included_sheets": ["Sheet1", "Sheet2"],
      "data_range": "A1:H200",
      "header_row": 1,
      "column_information": {
        "name": "A",
        "studio": "C",
        "release_date": "D"
      }
    }
  }
}
```

### Exemple Multiple Sheets Avec Layout Par Onglet

```json
{
  "file_type": "libreoffice_ods",
  "multiple_sheets_conf": {
    "sheets": [
      {
        "sheet_name": "Playstation",
        "sheet_information": "platform",
        "data_range": "A1:H200",
        "header_row": 1,
        "column_information": {
          "name": "A",
          "studio": "C",
          "release_date": "D"
        }
      }
    ]
  }
}
```

## Règles De Plage Et Colonnes

- `data_range` utilise le format tableur `A1:H200`.
- Les bornes de `data_range` sont inclusives.
- `header_row` est un entier et utilise l'index tableur commençant à `1`.
- `header_row` doit appartenir à `data_range`.
- `column_information` utilise des lettres de colonnes tableur : `A`, `B`,
  `AA`, etc.
- Les colonnes déclarées doivent appartenir à `data_range`.

## Règles Sur Les Onglets

- En mode `shared_layout`, `included_sheets` est optionnel.
- Si `included_sheets` est absent, tous les onglets du fichier sont importés.
- La notion d'onglet technique n'existe plus.
- En mode `sheets`, les onglets à importer sont ceux déclarés dans la liste
  `sheets`.
- `sheets[].sheet_name` est obligatoire et non vide.
- Quand `sheet_information` vaut `platform`, `studio` ou une future valeur de
  l'enum, la valeur du champ porté par l'onglet est toujours le nom de l'onglet
  importé.
- L'information portée par l'onglet ne doit pas aussi être présente dans
  `column_information`.

## Validations 422

Retourner `422` avec :

```json
{
  "error": "Configuration invalide.",
  "details": ["message explicite"]
}
```

Cas à couvrir :

- `collection_file_description` absent ;
- JSON absent ou invalide ;
- `file_type` inconnu ;
- `single_sheet_conf` et `multiple_sheets_conf` présents ensemble ;
- `multiple_sheets_conf` avec `shared_layout` et `sheets` présents ensemble ;
- aucun mode présent ;
- champ obligatoire non mappé ;
- colonne hors `data_range` ;
- `header_row` hors `data_range` ;
- `sheet_information` inconnu ;
- `sheet_information` présent aussi dans `column_information` ;
- `included_sheets` contient un onglet absent du fichier ;
- `sheets[].sheet_name` absent ou vide.

## Tests Attendus

Ajouter ou modifier des tests backend pour valider :

- configuration absente -> `422` ;
- JSON invalide -> `422` ;
- `file_type` inconnu -> `422` ;
- conflit entre modes -> `422` ;
- colonne obligatoire manquante -> `422` ;
- colonne hors `data_range` -> `422` ;
- `header_row` hors `data_range` -> `422` ;
- `sheet_information` inconnu -> `422` ;
- information portée par l'onglet aussi présente en colonne -> `422` ;
- `included_sheets` avec onglet absent -> `422` ;
- `sheets[].sheet_name` absent ou vide -> `422`.

## Critères D'Acceptation

- Le contrat JSON est représenté par des DTOs ou objets dédiés.
- Les validations retournent toutes `422` avec `error` et `details`.
- Aucune validation de configuration n'est codée dans le controller.
- Les tests backend ciblés passent.
