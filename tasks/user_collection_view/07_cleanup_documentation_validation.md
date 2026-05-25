# 07 - Nettoyage, documentation et validation

## Objectif

Finaliser la suppression de l'ancien fonctionnement ODS hors import, mettre à
jour la documentation et valider l'ensemble du périmètre.

Cette tâche doit s'appuyer sur le rapport :

`tasks/user_collection_view/00_existing_code_analysis_result.md`

## Nettoyage backend

1. Lire et prendre en compte
   `tasks/user_collection_view/00_existing_code_analysis_result.md`.
2. Supprimer les services ou méthodes ODS devenus inutiles hors import.
3. Conserver uniquement les composants ODS nécessaires :
   - à l'import utilisateur ;
   - au téléchargement brut du fichier utilisateur, sans parsing.
4. Supprimer `GamesService` et `AddGameChoiceService` si plus aucune fonction
   utile à l'import ne les utilise.
5. Si des fonctions ODS restent utiles à l'import, les regrouper dans
   `services/collection/ods/UserCollectionODSReader`.
6. Vérifier qu'aucune consultation collection ne dépend de :
   - `JEUXVIDEO_ODS_PATH`
   - `GamesService`
   - `OdsReader`
   - `read_games_dataframe`
   - `OdsCache`
   - `OdsImageReader`
   - `OdsXmlReader`
   - `OdsPathResolver`

## Documentation

1. Mettre à jour `README.md`.
2. Mettre à jour `documentation/backend-api.md`.
3. Mettre à jour `documentation/backend-arch.md`.
4. Mettre à jour `documentation/frontend-arch.md`.
5. Mettre à jour `documentation/site-plan.md` si les routes frontend changent.
6. Mettre à jour `documentation/menu.md` si la navigation change.
7. Mettre à jour `documentation/database.md` uniquement si le contrat SQL ou les
   responsabilités autour de `t_user_collection` doivent être précisées.
8. Mettre à jour toute documentation mentionnant :
   - la page wishlist ;
   - la lecture ODS de consultation ;
   - l'ancien endpoint `/collections/videogames/home` ;
   - l'ancien endpoint `/collections/videogames/search` ;
   - les anciens endpoints de plateforme ODS.

## Validation complète

1. Lancer les tests backend.
2. Lancer le build frontend.
3. Vérifier les diffs.
4. Rechercher les anciens endpoints supprimés.
5. Rechercher les anciens usages ODS hors import.
6. Rebuild les images Docker backend et web si le runtime change.

## Critères d'acceptation

- La documentation reflète le nouveau fonctionnement SQL.
- Le README ne décrit plus les anciennes consultations ODS.
- Les endpoints supprimés ne sont plus documentés comme disponibles.
- Les validations backend et frontend passent.
- Les images Docker concernées sont reconstruites.
- Les écarts éventuels avec le rapport d'analyse sont documentés dans le bilan
  final.

## Commandes de validation attendues

```bash
./test_backend.sh
npm run build
git diff --check
docker compose -f docker/docker-compose.local.yml build backend web
```
