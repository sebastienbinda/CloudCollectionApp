# 00 - Analyse du code existant et architecture proposée

## Objectif

Analyser la consultation frontend de collection, la navigation applicative et
les contrats wishlist déjà disponibles avant toute modification applicative,
puis produire le rapport d'architecture cible pour la page `/wishlist`.

Cette tâche ne doit pas modifier le code applicatif.

## Documentation À Lire

- `documentation/collection.md`
- `documentation/frontend-arch.md`
- `documentation/site-plan.md`
- `documentation/menu.md`
- `documentation/backend-api.md`
- `tasks/0.2.0/user_wishlist_view/user_wishlist_view.md`

## Analyse Frontend

Identifier et documenter :

- la route frontend actuelle de `Ma collection` ;
- la route frontend actuelle de la page plateforme ;
- le composant de rendu de la page plateforme ;
- le hook qui charge les jeux d'une plateforme ;
- le service frontend qui appelle
  `GET /collections/videogames/games/search` ;
- le mapping de colonnes fait par le frontend pour les jeux de collection ;
- les composants de tableau, filtre et tri déjà réutilisables ;
- le composant de menu principal et ses règles d'accès ;
- le view model applicatif qui orchestre la navigation et les props de vues ;
- les styles existants utilisables pour éviter une nouvelle charte visuelle.

## Analyse Des Contrats Existants

Confirmer dans le rapport :

- que le backend expose déjà le filtre `wishlist=true` sur
  `GET /collections/videogames/games/search` ;
- qu'aucun nouveau endpoint backend n'est nécessaire ;
- que la page collection existante doit continuer à demander
  `wishlist=false` ;
- que la page wishlist doit demander `wishlist=true` ;
- que `VideoGamesApi.fetchGames` doit être rendu paramétrable au lieu de créer
  une méthode dédiée wishlist ;
- que les tris de listes collection/wishlist doivent être demandés au backend
  via `sort` et non recalculés côté frontend ;
- que le champ technique `wishlist` ne doit pas être affiché ;
- que la colonne `Plateforme` est une information non cliquable ;
- que la page wishlist n'a ni sélecteur de plateforme ni actions de ligne.

## Architecture Cible À Proposer

Le rapport doit proposer les noms exacts des fichiers, composants, hooks,
fonctions et méthodes à créer ou modifier pour :

- ajouter la route frontend `/wishlist` ;
- ajouter l'entrée de menu `Liste de souhaits` conformément à
  `documentation/menu.md` ;
- factoriser le rendu commun entre page plateforme et page wishlist ;
- garder les actions et le sélecteur plateforme uniquement sur la page
  plateforme ;
- charger les données wishlist avec `wishlist=true` ;
- limiter les colonnes wishlist à :
  - `Nom du jeu`
  - `Plateforme`
  - `Studio`
  - `Date de sortie`
  - `Version`
- filtrer la wishlist par `Plateforme` ;
- trier la wishlist par `Nom du jeu`, `Plateforme`, `Studio` et
  `Date de sortie` ;
- appliquer le tri par défaut sur `Nom du jeu` en ordre alphabétique ;
- convertir les tris frontend en paramètres backend `sort` ;
- gérer les états vide, chargement et erreur.

## Questions À Fermer Dans Le Rapport

Le rapport doit confirmer ou signaler explicitement :

- si l'entrée `Liste de souhaits` est visible et désactivée sans session, ou
  masquée, en tenant compte de `documentation/menu.md` ;
- l'ordre exact de l'entrée `Liste de souhaits` dans le menu ;
- si la page wishlist est accessible aux profils `ADMIN` ou suit les mêmes
  restrictions que `Ma collection` ;
- les documents à mettre à jour en fin de chantier ;
- les validations frontend à exécuter.

## Livrable

Créer le fichier :

```text
tasks/0.2.0/user_wishlist_view/00_existing_code_analysis_result.md
```

Le rapport doit contenir :

- une cartographie du code existant ;
- l'architecture proposée ;
- les noms des fichiers et fonctions à modifier ;
- les risques identifiés ;
- les décisions de contrat à reprendre dans les sous-tâches suivantes ;
- les écarts éventuels avec la tâche chapeau.

## Critères D'Acceptation

- Le rapport existe.
- Le rapport ne modifie pas le code applicatif.
- Les règles de `documentation/frontend-arch.md`, `documentation/site-plan.md`
  et `documentation/menu.md` sont prises en compte.
- Les sous-tâches suivantes peuvent être réalisées sans nouvelle exploration
  générale.
- Les choix d'architecture et de nommage sont suffisamment précis pour guider
  l'implémentation.
