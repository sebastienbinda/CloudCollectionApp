# 05 - Service d'import de collection utilisateur

## Objectif

Créer le service métier responsable de l'import complet de la collection utilisateur.

## Étapes

1. Créer un service backend d'import de collection utilisateur.
2. Vérifier que l'utilisateur connecté n'a pas déjà une valeur dans `t_user.collection_file_path`.
3. Refuser l'import avec une erreur métier correspondant au HTTP `409` si une collection existe déjà.
4. Vérifier le type de fichier attendu.
5. Vérifier la taille maximale configurée.
6. Copier le fichier vers `/users/workspace/<user_id>/<user_id>-collection.ods`.
7. Appliquer les droits `0440` sur le fichier copié.
8. Lire le fichier avec le service ODS dédié.
9. Créer les plateformes inexistantes.
10. Créer les studios inexistants.
11. Créer les jeux inexistants selon le couple `(name, platform)`.
12. Créer les associations manquantes dans `t_user_collection`.
13. Ne jamais remplacer les données existantes.
14. Mettre à jour `t_user.collection_file_path` en fin d'import réussi.
15. Garantir l'atomicité de l'import en base.
16. Supprimer le fichier copié si l'import échoue.

## Critères d'acceptation

- L'import est entièrement transactionnel côté base.
- Aucun état partiel n'est conservé en cas d'échec.
- Le fichier copié est supprimé en cas d'échec.
- Le service retourne les compteurs attendus :
   - plateformes créées
   - studios créés
   - jeux créés
   - jeux associés
- Le service ne dépend pas directement de la couche HTTP.

## Validation attendue

- Ajouter ou mettre à jour les tests unitaires backend.
- Tester :
   - import nominal
   - collection déjà importée
   - fichier invalide
   - fichier trop volumineux
   - rollback en cas d'échec
   - suppression du fichier en cas d'échec
   - associations avec jeux déjà existants
