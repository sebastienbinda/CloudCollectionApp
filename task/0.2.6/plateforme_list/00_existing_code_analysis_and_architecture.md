# 00 - Analyse du code existant et architecture proposée

## Objectif

Analyser le fonctionnement actuel des plateformes, de l'import utilisateur, de
la Bibliothèque publique et des écrans frontend avant toute modification
applicative.

Cette tâche ne doit pas modifier le code applicatif. Elle doit produire le
rapport d'architecture utilisé par toutes les sous-tâches suivantes.

## Documentation À Lire

- `task/0.2.6/plateforme_list/plateforme_list.md`
- `documentation/database.md`
- `documentation/import.md`
- `documentation/backend-api.md`
- `documentation/backend-arch.md`
- `documentation/frontend-arch.md`
- `documentation/site-plan.md`
- `documentation/authentication.md`

## Analyse Backend

Identifier et documenter :

- le modèle ORM `Platform` et les colonnes actuellement exposées ;
- les migrations Alembic existantes liées à `t_platform`, `t_game` et
  `t_user_collection` ;
- les repositories qui lisent ou écrivent `t_platform` ;
- le service et le repository d'import utilisateur qui créent actuellement les
  plateformes absentes ;
- les objets de résultat d'import et les compteurs retournés au frontend ;
- les endpoints de plateformes concernés :
  - Bibliothèque publique ;
  - collection utilisateur ;
  - recherche ou liste de plateformes utilisées par les écrans ;
- les services d'envoi d'email existants et leur configuration `.env` ;
- les patterns existants de lecture et validation de variables
  d'environnement ;
- les tests backend déjà présents sur plateformes, import, Bibliothèque et
  notifications.

## Analyse Frontend

Identifier et documenter :

- les services API frontend qui chargent les plateformes ;
- les hooks de chargement et de sélection de plateformes ;
- les composants affichant les listes de plateformes ;
- les composants de résumé d'import ;
- les styles mobile déjà utilisés pour les cartes de jeux ;
- les pages qui consomment les champs `release_date`, `manufacturer`,
  `description` ou `status`.

## Architecture Cible À Proposer

Le rapport doit proposer les noms exacts des fichiers, classes, méthodes,
fonctions et tests à créer ou modifier pour :

- le nouveau schéma `t_platform` avec `end_date` et sans colonne obsolète ;
- le chargement initial des plateformes depuis
  `task/0.2.6/plateforme_list/consoles_jeux_video.csv` ;
- la stratégie de migration compatible avec les règles de
  `documentation/database.md` ;
- la stratégie de parsing des dates CSV, y compris `Inconnue` et `En vente` ;
- le mapping d'une plateforme importée vers le référentiel applicatif ;
- le calcul du score de correspondance en cas de coquille ;
- les seuils imposés par la tâche chapeau et le comportement de chaque tranche ;
- la configuration `.env` des seuils via `MATCHING_LOW_LVL_RATING` et
  `MATCHING_HIGH_LEVEL_RATING` ;
- la forme exacte des warnings d'import pour les plateformes non rattachées ;
- le contenu de l'email administrateur ;
- les compteurs d'import à renommer ou ajouter ;
- le format API cible des plateformes ;
- les changements frontend ;
- les tests backend et frontend à créer ou modifier ;
- les validations et rebuild Docker attendus.

## Questions À Fermer Dans Le Rapport

Le rapport doit trancher explicitement :

- si une migration peut vider `t_game` et `t_platform`, ou si elle doit rester
  idempotente et préserver les données existantes ;
- si `release_date` et `manufacturer` peuvent être `NULL` en base quand le CSV
  contient une valeur inconnue, malgré le tableau de la tâche chapeau ;
- si `end_date = NULL` représente une date inconnue ou une plateforme encore en
  vente ;
- si la colonne `status` doit être supprimée partout ou conservée pour
  compatibilité ;
- la règle d'arbitrage en cas d'égalité de score ;
- le comportement d'import quand aucune plateforme fiable n'est trouvée :
  ignorer les jeux, rejeter l'import, ou importer partiellement avec warnings ;
- la variable d'environnement qui contient l'email administrateur ;
- les valeurs par défaut et règles de validation des variables
  `MATCHING_LOW_LVL_RATING` et `MATCHING_HIGH_LEVEL_RATING` ;
- les documents à mettre à jour en fin de chantier.

## Livrable

Créer le fichier :

```text
task/0.2.6/plateforme_list/00_existing_code_analysis_result.md
```

Le rapport doit contenir :

- une cartographie du code existant ;
- l'architecture cible proposée ;
- les décisions de contrat qui bloquent ou guident les autres sous-tâches ;
- les noms des fichiers, classes, méthodes, composants et tests à modifier ;
- les risques identifiés ;
- les écarts éventuels entre la tâche chapeau et les règles documentées ;
- les validations à exécuter.

## Critères D'Acceptation

- Le rapport existe.
- Le rapport ne modifie pas le code applicatif.
- Les décisions sont suffisamment précises pour réaliser les sous-tâches sans
  nouvelle analyse générale.
- Les conflits éventuels avec `documentation/*.md` sont explicitement listés.
