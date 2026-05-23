# 06 - Endpoints backend utilisateur

## Objectif

Exposer les endpoints nécessaires au frontend pour connaître et importer la collection utilisateur.

## Étapes

1. Ajouter `GET /api/users/me/collection` dans le contrôleur utilisateur approprié.
2. Retourner :
   ```json
   {
     "has_collection": true
   }
   ```
   ou :
   ```json
   {
     "has_collection": false
   }
   ```
3. Ajouter `POST /api/users/import`.
4. Accepter le format `multipart/form-data`.
5. Lire le paramètre `collection_file`.
6. Protéger les deux endpoints avec le profil `USER`.
7. Appeler le service métier d'import depuis le contrôleur.
8. Mapper les erreurs métier vers les codes HTTP attendus :
   - `201`
   - `400`
   - `403`
   - `409`
   - `413`
   - `500`

## Critères d'acceptation

- Les endpoints ne contiennent pas de logique métier lourde.
- Les endpoints utilisent les services existants ou nouvellement créés.
- Les réponses JSON respectent `tasks/user_collection/user_collection_workflow.md`.
- Les routes sont protégées conformément à la documentation d'authentification.

## Validation attendue

- Ajouter ou mettre à jour les tests backend des routes.
- Tester les réponses avec et sans collection.
- Tester les erreurs HTTP principales.
