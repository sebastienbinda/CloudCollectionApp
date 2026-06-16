# 07 - Tests backend approfondis

## Objectif

Centraliser les tests backend de non-régression pour le nouveau référentiel de
plateformes et le mapping d'import.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.6/plateforme_list/00_existing_code_analysis_result.md`
- les tâches backend `02`, `03`, `04` et `05`.

## Tests À Couvrir

Ajouter ou compléter les tests backend pour valider :

- schéma `t_platform` ;
- chargement du catalogue plateformes ;
- endpoint public de liste / recherche plateformes ;
- endpoint collection de recherche plateformes ;
- cache serveur du catalogue plateformes avec TTL 5 heures ;
- absence de requêtes SQL répétées pour le catalogue plateformes avant
  expiration du cache ;
- import avec rattachement exact ;
- import avec casse différente ;
- import avec accents différents ;
- import avec espaces différents ;
- import avec coquille acceptée ;
- import avec score entre 25% et 75%, warning et email administrateur ;
- import refusé avec score inférieur à 25% ;
- import refusé avec score à 0% ;
- seuils par défaut `MATCHING_LOW_LVL_RATING=25` et
  `MATCHING_HIGH_LEVEL_RATING=75` ;
- seuils personnalisés par variables d'environnement ;
- refus d'une configuration de seuils non numérique ;
- refus d'une configuration avec seuil bas supérieur ou égal au seuil haut ;
- refus d'une configuration hors bornes `0..100` ;
- import avec correspondance ambiguë ;
- warnings d'import ;
- email administrateur ;
- absence de création de plateforme par l'import ;
- utilisation du cache plateformes pendant l'import ;
- reset Bibliothèque admin sans suppression de `t_platform` ;
- réinitialisation collection utilisateur sans suppression de `t_platform` ;
- invalidation du cache plateformes après reset Bibliothèque et après import
  créant des jeux ;
- compteur de plateformes liées.

## État Branche `list_platform` - 2026-06-16

Les tests backend de la branche couvrent désormais les points suivants :

- schéma `t_platform`, `t_platform_alias` et seed catalogue CSV via
  `backend/tests/test_database_schema_service.py` et
  `backend/tests/test_platform_catalog_seed_service.py` ;
- chargement du catalogue plateformes et alias via
  `backend/tests/test_platform_catalog_csv_reader.py`,
  `backend/tests/test_platform_alias_catalog_csv_reader.py` et
  `backend/tests/test_platform_catalog_seed_service.py` ;
- endpoint public plateformes et endpoint collection plateformes via
  `backend/tests/test_library_routes.py` et
  `backend/tests/test_collection_routes.py` ;
- cache serveur plateformes, TTL et absence de requêtes SQL répétées via
  `backend/tests/test_platform_catalog_cache.py` ;
- matching exact, casse, accents, espaces, coquille acceptée, warning manuel,
  refus score bas, refus score nul et ambiguïté via
  `backend/tests/test_platform_matching_service.py` ;
- seuils par défaut, variables d'environnement et configurations invalides via
  `backend/tests/test_platform_matching_configuration.py` ;
- warnings d'import et email administrateur via
  `backend/tests/test_platform_matching_admin_notifier.py` et
  `backend/tests/test_user_collection_import_wishlist_result.py` ;
- absence de création de plateforme par l'import, utilisation du catalogue
  pendant l'import, propagation des warnings de matching et compteur de
  plateformes liées via
  `backend/tests/test_user_collection_import_platform_matching_repository.py` ;
- reset Bibliothèque sans suppression de `t_platform` et réinitialisation
  collection utilisateur sans suppression du référentiel global via
  `backend/tests/test_library_reset_repository.py` et
  `backend/tests/test_user_collection_reinitialization_repository.py` ;
- invalidation du cache plateformes après import créant des jeux via
  `backend/tests/test_user_collection_import_platform_matching_repository.py`.

La tâche 7 doit être considérée réalisée quand `./test_backend.sh` passe ou que
les échecs non liés sont listés explicitement.

## Validation

Lancer :

```bash
./test_backend.sh
```

Si la suite complète est trop longue, lancer d'abord les tests ciblés puis la
suite complète avant clôture de la fonctionnalité.

## Critères D'Acceptation

- Les tests ciblés existent.
- Les tests couvrent les cas de coquille demandés par la tâche chapeau.
- `./test_backend.sh` passe ou les échecs non liés sont explicitement listés.
