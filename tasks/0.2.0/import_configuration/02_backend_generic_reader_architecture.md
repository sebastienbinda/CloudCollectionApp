# 02 - Architecture backend générique des readers

## Objectif

Introduire l'architecture générique de lecture de fichiers de collection et y
brancher le reader LibreOffice ODS actuel.

Cette tâche dépend de :

- `00_existing_code_analysis_result.md`
- `01_import_configuration_contract.md`

## Éléments À Créer Ou Adapter

Créer ou adapter :

- `CollectionFileReader` : interface ou protocole générique ;
- `CollectionFileDescription` : DTO d'entrée validé ;
- un DTO de sortie générique déjà compatible avec l'import SQL actuel ;
- `CollectionFileReaderFactory` : sélection par `file_type` ;
- une implémentation `libreoffice_ods` basée sur l'ancien
  `OdsCollectionImportReader`.

## Règles D'Architecture

- `UserCollectionImportService` dépend d'une abstraction générique, pas d'un
  reader ODS concret.
- Les références ODS restent dans l'implémentation ODS et dans la factory.
- Le service d'import utilisateur ne connaît pas les détails `data_range`,
  colonnes tableur ou onglets.
- La sortie du reader doit rester stable pour les futurs readers Excel.
- Aucun ancien fallback sur une structure ODS codée en dur ne doit rester.

## Comportement Reader ODS

Le reader `libreoffice_ods` doit utiliser la configuration validée pour lire :

- un fichier à feuille unique ;
- plusieurs feuilles avec `shared_layout` ;
- plusieurs feuilles avec configuration par feuille.

Le reader doit produire les mêmes informations métier qu'avant :

- plateformes ;
- studios ;
- jeux avec `name`, `platform`, `studio`, `release_date`.

## Tests Attendus

Ajouter ou modifier des tests backend pour valider :

- un reader ODS configurable lit un import `single_sheet_conf` valide ;
- un reader ODS configurable lit un import `shared_layout` valide ;
- un reader ODS configurable lit un import `sheets` valide ;
- le reader applique le nom d'onglet comme valeur du champ porté par
  `sheet_information` ;
- il est possible de remplacer le reader ODS par un faux reader, par exemple
  un reader ASCII, sans modifier `UserCollectionImportService`.

## Critères D'Acceptation

- L'interface générique existe.
- La factory sélectionne le reader via `file_type`.
- L'import ODS ne dépend plus d'une structure fixe dans le code.
- Les tests backend ciblés passent.
