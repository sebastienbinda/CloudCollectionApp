# 00 - Analyse du code existant et architecture proposée

## Objectif

Analyser le workflow d'import actuel avant toute modification et proposer
l'architecture cible permettant un import configurable et extensible à plusieurs
types de fichiers.

Cette tâche ne doit pas modifier le code applicatif.

## Documentation À Lire

- `documentation/import.md`
- `documentation/backend-api.md`
- `documentation/backend-arch.md`
- `documentation/frontend-arch.md`
- `documentation/database.md`
- `documentation/site-plan.md`
- `tasks/import_configuration/import_configuration.md`

## Analyse Backend

Identifier et documenter :

- le controller qui reçoit `POST /api/users/import` ;
- le service qui orchestre l'import utilisateur ;
- le reader ODS actuel ;
- les DTOs ou modèles déjà utilisés pour transporter les données importées ;
- les repositories qui persistent `t_user.collection_file_path`,
  `t_user.collection_file_description`, `t_user_collection`, `t_game`,
  `t_platform` et `t_studio` ;
- les tests backend existants autour de l'import.

## Analyse Frontend

Identifier et documenter :

- la page d'onboarding actuelle ;
- le hook qui orchestre l'import ;
- le service frontend qui appelle `POST /api/users/import` ;
- les tests ou validations frontend existants.

## Architecture Cible À Proposer

Le rapport doit proposer :

- une interface ou un protocole `CollectionFileReader` ;
- un DTO d'entrée `CollectionFileDescription` ;
- un DTO de sortie générique compatible avec l'import SQL actuel ;
- une factory `CollectionFileReaderFactory` basée sur `file_type` ;
- une implémentation ODS, par exemple en renommant ou encapsulant
  `OdsCollectionImportReader` ;
- l'endroit exact où valider la configuration avant import ;
- l'endroit exact où sauvegarder `collection_file_description` après succès ;
- les fichiers de tests à créer ou modifier.

## Règles D'Architecture

- `UserCollectionImportService` ne doit pas dépendre directement d'un reader ODS.
- Toute référence ODS doit rester dans la factory ou dans l'implémentation ODS.
- Le modèle de sortie du reader doit rester indépendant du type de fichier.
- L'import doit rester transactionnel.

## Livrable

Créer un fichier :

```text
tasks/import_configuration/00_existing_code_analysis_result.md
```

Le rapport doit contenir :

- une cartographie du code existant ;
- l'architecture proposée ;
- les risques identifiés ;
- les tests à prévoir ;
- les écarts éventuels avec la tâche chapeau.

## Critères D'Acceptation

- Le rapport existe.
- L'architecture proposée respecte `documentation/backend-arch.md`.
- Les dépendances ODS actuelles sont clairement identifiées.
- Les sous-tâches suivantes peuvent être réalisées sans nouvelle phase
  d'exploration générale.
