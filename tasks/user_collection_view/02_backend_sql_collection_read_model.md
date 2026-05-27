# 02 - Lecture SQL de collection utilisateur

## Objectif

Créer la couche backend de lecture SQL de la collection utilisateur, sans
lecture ODS et sans changement frontend.

Cette tâche doit s'appuyer sur le rapport :

`tasks/user_collection_view/00_existing_code_analysis_result.md`

## Étapes

1. Lire et prendre en compte
   `tasks/user_collection_view/00_existing_code_analysis_result.md`.
2. Rechercher les implémentations existantes de pagination, tri et filtres dans
   la Bibliothèque.
3. Réutiliser le parseur de requêtes et les conventions de pagination existants
   autant que possible.
4. Créer ou étendre les repositories SQL nécessaires pour lire :
   - les statistiques globales de collection utilisateur ;
   - les plateformes associées à l'utilisateur connecté ;
   - les jeux associés à l'utilisateur connecté.
5. Filtrer toutes les requêtes par `user_id`.
6. Joindre les tables nécessaires :
   - `t_user_collection`
   - `t_game`
   - `t_platform`
   - `t_studio`
7. Implémenter les filtres plateformes :
   - `name` en contains sans casse et sans accents.
8. Implémenter les filtres jeux :
   - `name` en contains sans casse et sans accents ;
   - `studio_name` en contains sans casse et sans accents ;
   - `platform_name` en contains sans casse et sans accents ;
   - `platform_id` exact ;
   - `release_date=YYYY-MM-DD..YYYY-MM-DD`.
9. Implémenter les tris autorisés :
   - plateformes : `name` ;
   - jeux : `name`, `platform_name`, `release_date`, `studio_name`,
     `buy_date`, `grade`.
10. Pour les champs futurs non stockés actuellement, retourner une valeur vide :
   - `version`
   - `buy_date`
   - `buy_location`
   - `grade`
11. Créer un service métier de consultation, par exemple
    `UserCollectionQueryService`, qui expose les cas d'usage sans dépendre de
    Flask.

## Contrats de sortie

### Statistiques globales

```json
{
  "total": 0,
  "total_value": 0,
  "average_value": 0,
  "max_platform": ""
}
```

### Plateformes

```json
{
  "page": {
    "totalElements": 10,
    "page": 0,
    "size": 500,
    "totalPages": 1
  },
  "platforms": [
    {
      "id": 1,
      "name": "Switch",
      "nb_games": 25,
      "total_value": 0,
      "average_value": 0
    }
  ]
}
```

### Jeux

```json
{
  "page": {
    "totalElements": 10,
    "page": 0,
    "size": 500,
    "totalPages": 1
  },
  "games": [
    {
      "id": 1,
      "name": "",
      "platform_name": "",
      "platform_id": 1,
      "release_date": "",
      "studio_name": "",
      "studio_id": 10,
      "version": "",
      "buy_date": "",
      "buy_location": "",
      "grade": ""
    }
  ]
}
```

## Critères d'acceptation

- Aucune lecture ODS n'est utilisée par le service de consultation.
- Les résultats sont strictement filtrés par utilisateur connecté.
- Un utilisateur sans collection reçoit les réponses vides attendues.
- `platform_id` invalide ou non associé à l'utilisateur retourne une liste de
  jeux vide.
- Les filtres texte sont sans casse et sans accents.
- La pagination et le tri suivent les règles de la Bibliothèque.
- Les fichiers, classes et repositories modifiés correspondent à l'architecture
  validée dans le rapport d'analyse.

## Validation attendue

- Ajouter ou mettre à jour les tests backend sur la couche service/repository.
- Tester :
   - statistiques avec collection ;
   - statistiques sans collection ;
   - plateformes utilisateur ;
   - jeux utilisateur ;
   - isolation entre deux utilisateurs ;
   - recherche sans casse et sans accents ;
   - pagination ;
   - tri ;
   - filtre `platform_id` ;
   - plage `release_date`.
