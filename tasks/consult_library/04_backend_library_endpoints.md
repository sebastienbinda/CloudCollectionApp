# 04 - Endpoints backend Bibliothèque

## Objectif

Exposer les endpoints publics de consultation de la Bibliothèque.

## Étapes

1. Ajouter un contrôleur Bibliothèque selon les conventions Flask existantes.
2. Exposer `GET /api/library/entities`.
3. Exposer `GET /api/library/platforms`.
4. Exposer `GET /api/library/studios`.
5. Exposer `GET /api/library/games`.
6. Brancher les paramètres `name`, `page`, `size` et `sort` sur la couche de service.
7. Garantir que ces routes ne nécessitent pas d'authentification.
8. Garantir que les réponses JSON respectent `tasks/consult_library/consult.md`.
9. Ajouter les tests de routes backend.

## Critères d'acceptation

- Les quatre endpoints répondent sans token.
- Les endpoints sont strictement en lecture seule.
- Les réponses de pagination contiennent `totalElements`, `page`, `size` et `totalPages`.
- Les erreurs de paramètres invalides retombent sur les valeurs par défaut prévues.
- Aucun champ privé ou utilisateur n'est exposé.

## Validation attendue

- Lancer les tests backend des routes.
- Lancer `./test_backend.sh`.
- Mettre à jour `documentation/backend-api.md` dans la tâche documentation.
