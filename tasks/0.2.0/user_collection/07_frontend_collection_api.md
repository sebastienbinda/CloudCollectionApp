# 07 - API frontend collection utilisateur

## Objectif

Ajouter la couche frontend qui appelle les endpoints backend de collection utilisateur.

## Étapes

1. Identifier la structure actuelle des appels API frontend.
2. Ajouter une fonction d'appel pour `GET /api/users/me/collection`.
3. Ajouter une fonction d'appel pour `POST /api/users/import`.
4. Envoyer l'upload en `multipart/form-data`.
5. Centraliser la gestion des erreurs utiles :
   - fichier invalide
   - fichier trop volumineux
   - collection déjà importée
   - utilisateur non autorisé
   - erreur inattendue

## Critères d'acceptation

- Les appels API respectent l'architecture frontend existante.
- Aucun composant React ne construit manuellement les URLs si une couche API existe déjà.
- Les erreurs backend sont exploitables par l'interface.

## Validation attendue

- Lancer les tests frontend s'ils existent.
- Lancer le build frontend.
