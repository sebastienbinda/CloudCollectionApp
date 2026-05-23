# 08 - Onboarding frontend et import

## Objectif

Afficher le tutoriel d'import pour les utilisateurs qui n'ont pas encore de collection.

## Étapes

1. Après connexion, appeler `GET /api/users/me/collection`.
2. Si `has_collection` vaut `true`, conserver la redirection actuelle vers l'accueil.
3. Si `has_collection` vaut `false`, afficher une page ou vue d'onboarding collection.
4. Ajouter un bouton d'upload du fichier ODS.
5. Appeler `POST /api/users/import` après sélection du fichier.
6. Afficher un état de chargement pendant l'import.
7. Afficher les erreurs utilisateur selon le code HTTP retourné.
8. Rediriger vers l'accueil après import réussi.
9. Respecter `documentation/site-plan.md` pour toute page ou route frontend ajoutée.

## Critères d'acceptation

- Un utilisateur sans collection voit le parcours d'import.
- Un utilisateur avec collection garde le parcours actuel.
- L'upload bloque les doubles soumissions pendant l'import.
- Les erreurs principales sont compréhensibles côté interface.
- La redirection vers l'accueil fonctionne après succès.

## Validation attendue

- Lancer le build frontend.
- Vérifier manuellement :
   - utilisateur sans collection
   - utilisateur avec collection
   - import réussi
   - import refusé
   - fichier trop volumineux
