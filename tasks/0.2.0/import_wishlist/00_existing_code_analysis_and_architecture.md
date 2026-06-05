# 00 - Analyse du code existant et architecture proposée

## Objectif

Analyser le workflow actuel d'import, la consultation SQL de collection et les
contrats frontend avant toute modification applicative, puis proposer
l'architecture cible pour intégrer l'information `wishlist`.

Cette tâche ne doit pas modifier le code applicatif.

## Documentation À Lire

- `documentation/import.md`
- `documentation/backend-api.md`
- `documentation/backend-arch.md`
- `documentation/frontend-arch.md`
- `documentation/database.md`
- `documentation/site-plan.md`
- `tasks/0.2.0/import_wishlist/import_wishlist.md`

## Analyse Backend

Identifier et documenter :

- le controller qui reçoit `POST /api/users/import` ;
- le service qui orchestre l'import utilisateur ;
- les DTOs de configuration d'import existants ;
- les DTOs représentant les lignes importées ;
- les readers et factories utilisés par type de fichier ;
- les repositories qui persistent `t_user_collection`, `t_game`, `t_platform`,
  `t_studio` et `t_user.collection_file_description` ;
- le repository et le service de consultation SQL de collection ;
- les endpoints impactés :
  - `POST /api/users/import`
  - `GET /collections/videogames`
  - `GET /collections/videogames/games/search`
- les tests backend existants à modifier ou compléter.

## Analyse Frontend

Identifier et documenter :

- le composant de page d'onboarding import ;
- le hook qui orchestre l'upload, l'analyse, la configuration et l'import ;
- le builder de configuration d'import ;
- les composants de champs de configuration import ;
- le service frontend qui appelle les endpoints d'import ;
- le service frontend qui appelle les endpoints de consultation collection ;
- les endroits où le frontend redirige actuellement vers `/collection` après
  import ;
- les tests ou validations frontend existants, s'il y en a.

## Architecture Cible À Proposer

Le rapport doit proposer les noms exacts des classes, fonctions, composants ou
fichiers à créer ou modifier, notamment pour :

- le contrat de configuration wishlist ;
- la validation du mode `wishlist.mode` ;
- le parsing des valeurs booléennes wishlist ;
- le transport de l'information `wishlist` dans les lignes importées ;
- la persistance de `t_user_collection.wishlist` ;
- les statistiques collection et wishlist ;
- le filtre `wishlist` de `GET /collections/videogames/games/search` ;
- les composants frontend de configuration wishlist ;
- l'écran de résumé post-import ;
- les tests backend et frontend à créer ou modifier.

## Questions À Fermer Dans Le Rapport

Le rapport doit confirmer ou proposer une règle explicite pour :

- la forme définitive des JSON `wishlist.mode = none`, `sheet` et `column` ;
- la priorité quand un même jeu apparaît à la fois en collection réelle et en
  wishlist ;
- les conséquences d'une valeur wishlist invalide sur les compteurs et la
  persistance ;
- la valeur SQL par défaut et la stratégie de migration ;
- le comportement par défaut de la page collection existante ;
- les documents à mettre à jour en fin de chantier.

## Livrable

Créer le fichier :

```text
tasks/0.2.0/import_wishlist/00_existing_code_analysis_result.md
```

Le rapport doit contenir :

- une cartographie du code existant ;
- l'architecture proposée ;
- les noms des classes, méthodes, composants et tests à créer ou modifier ;
- les risques identifiés ;
- les décisions de contrat à reprendre dans les sous-tâches suivantes ;
- les écarts éventuels avec la tâche chapeau.

## Critères D'Acceptation

- Le rapport existe.
- Le rapport respecte les règles de `documentation/backend-arch.md` et
  `documentation/frontend-arch.md`.
- Les sous-tâches suivantes peuvent être réalisées sans nouvelle phase
  d'exploration générale.
- Les choix d'architecture et de nommage sont suffisamment précis pour guider
  l'implémentation.
