# 04 - Suppression des anciennes routes ODS de collection

## Objectif

Supprimer les anciennes routes de consultation qui lisaient directement le
fichier ODS hors import.

Cette tâche doit s'appuyer sur le rapport :

`tasks/user_collection_view/00_existing_code_analysis_result.md`

## Routes à supprimer

- `GET /collections/videogames/home`
- `POST /collections/videogames/cache/reset`
- `GET /collections/videogames/search`
- `GET /collections/videogames/platforms`
- `GET /collections/videogames/column-values`
- `GET /collections/videogames/add-game-choices`
- `GET /collections/videogames/platform-image/<platform>`

## Étapes

1. Lire et prendre en compte
   `tasks/user_collection_view/00_existing_code_analysis_result.md`.
2. Supprimer l'enregistrement Flask de ces routes.
3. Supprimer les méthodes de controller devenues inutiles.
4. Supprimer les permissions frontend liées à ces routes si elles existent.
5. Vérifier que ces routes sont absentes de `/api/routes`.
6. Vérifier que ces routes retournent `404` parce qu'elles ne sont plus
   enregistrées.
7. Retirer les usages frontend de ces routes ou les remplacer dans les tâches
   frontend dédiées.

## Critères d'acceptation

- Les anciennes routes ODS ne sont plus enregistrées.
- Les anciennes routes ODS sont absentes de `/api/routes`.
- Aucun controller de consultation collection n'instancie `GamesService`,
  `OdsReader`, `OdsCache`, `OdsImageReader`, `OdsXmlReader` ou
  `OdsPathResolver`.
- La lecture ODS restante est limitée à l'import et au téléchargement brut du
  fichier utilisateur.
- Les suppressions correspondent à la cartographie des routes du rapport
  d'analyse.

## Validation attendue

- Ajouter ou mettre à jour les tests de routes backend.
- Tester l'absence de chaque endpoint supprimé.
- Vérifier par recherche code qu'aucune consultation collection ne lit l'ODS.
