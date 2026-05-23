# 09 - Documentation

## Objectif

Mettre à jour la documentation impactée par le workflow d'import de collection utilisateur.

## Étapes

1. Vérifier si `tasks/user_collection/user_collection_workflow.md` doit devenir la documentation fonctionnelle de référence.
2. Mettre à jour la documentation backend si de nouveaux services, contrôleurs ou conventions sont ajoutés.
3. Mettre à jour la documentation frontend si une nouvelle feature ou page est ajoutée.
4. Mettre à jour la documentation database si le comportement autour de `t_user.collection_file_path`, `t_user_collection`, plateformes, studios ou jeux doit être précisé.
5. Mettre à jour le README uniquement si nécessaire pour :
   - variables d'environnement
   - Docker
   - architecture globale
   - commandes de validation
   - routes ou fonctionnalités utilisateur majeures
6. Ajouter toute nouvelle documentation fonctionnelle uniquement après confirmation si elle crée un nouveau bloc documentaire.

## Critères d'acceptation

- Les changements de configuration sont documentés.
- Le README reste concis.
- Les documentations d'architecture restent alignées avec le code.
- Les règles de gouvernance documentaire du projet sont respectées.

## Validation attendue

- Relire les fichiers de documentation modifiés.
- Vérifier que les liens et chemins cités existent.
