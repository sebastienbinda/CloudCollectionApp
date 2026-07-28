# 00 - Analyse du code existant et architecture cible

## Objectif

Analyser l'existant avant toute modification applicative et confirmer
l'architecture cible pour le statut de validation des jeux Bibliothèque.

Cette tâche ne doit pas modifier le code applicatif. Elle doit produire le
rapport utilisé par les sous-tâches suivantes.

## Documentation À Lire

- `tasks/0.4.0/validate_new_game/task.md`
- `documentation/bibliotheque.md`
- `documentation/backend-api.md`
- `documentation/database.md`
- `documentation/site-plan.md`
- `documentation/authentication.md`
- `documentation/backend-arch.md`
- `documentation/frontend-arch.md`
- `documentation/menu.md`

## Analyse Backend

Identifier et documenter :

- les routes de consultation Bibliothèque des jeux, compteurs et détails ;
- les contrôleurs, services, repositories et serializers liés à `t_game` ;
- les chemins de création de jeux lors d'un import utilisateur ;
- les chemins de création de jeux lors d'un import CSV admin ;
- le reset Bibliothèque et la réutilisation du coeur d'import ;
- les mécanismes existants de modération d'images et de notification email ;
- les mécanismes existants de signalement de doublons et de notification
  quotidienne ;
- les patterns de pagination, filtres, route catalog et batch update ;
- les tests backend à créer ou modifier.

## Analyse Frontend

Identifier et documenter :

- la liste `/bibliotheque/jeux` et ses filtres existants ;
- le détail public `/bibliotheque/jeux/<game_id>` et l'accès depuis Collection ;
- le menu principal et la visibilité de l'entrée Bibliothèque ;
- la page Configuration et les actions admin existantes ;
- les hooks et services `LibraryApi`, `LibraryAdminApi` et route permissions ;
- les composants de tableau paginé et les patterns de sélection en masse ;
- les tests frontend à créer ou modifier.

## Contrat Cible À Confirmer

Le rapport doit préciser :

- le nom exact du nouveau champ `t_game.status` ;
- les valeurs autorisées `WAITING_VALIDATION` et `ACCEPTED` ;
- le statut initial des jeux existants lors de la migration ;
- les règles de visibilité pour anonyme, `GUEST`, `USER` et `ADMIN` ;
- le comportement de `GET /api/library/games` et
  `GET /api/library/games/<game_id>` ;
- les règles de visibilité des compteurs Bibliothèque et `total_games` des
  plateformes ;
- la stratégie de refus d'un jeu et l'impact sur `t_user_collection` ;
- la stratégie transactionnelle des validations/refus par lots ;
- le format des emails envoyés aux utilisateurs impactés ;
- l'endpoint ou le payload fournissant le compteur de jeux à valider ;
- les endpoints admin à créer et leurs droits ;
- les impacts documentaires à confirmer avant implémentation.

## Livrable

Créer le fichier :

```text
tasks/0.4.0/validate_new_game/00_existing_code_analysis_result.md
```

Le rapport doit contenir :

- une cartographie du code existant ;
- l'architecture cible proposée ;
- les décisions de contrat encore nécessaires, s'il en reste ;
- les risques et conflits éventuels avec `documentation/*.md` ;
- la liste des fichiers et tests probablement concernés.

## Critères D'Acceptation

- Le rapport existe.
- Aucun code applicatif n'est modifié.
- Les sous-tâches suivantes peuvent être réalisées sans nouvelle analyse
  générale.
