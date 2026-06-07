# 02 - Service backend et persistance transactionnelle

## Objectif

Implémenter la réinitialisation réelle de la collection côté backend.

Cette tâche dépend de :

- `01_backend_reinit_contract.md`

## Comportement Métier

Pour l'utilisateur connecté :

1. vérifier si une collection existe ;
2. supprimer les lignes `t_user_collection` de cet utilisateur ;
3. remettre `t_user.collection_file_path` à `NULL` ;
4. remettre `t_user.collection_file_description` à `NULL` ;
5. supprimer le fichier de collection associé sur disque quand il existe ;
6. retourner `200`.

Retourner `404` uniquement quand `collection_file_path` est `NULL` et qu'il
n'existe aucune entrée dans `t_user_collection` pour l'utilisateur.

## Transaction SQL

Les modifications SQL doivent être dans une transaction unique :

- suppression des associations utilisateur ;
- nettoyage des champs collection dans `t_user`.

Si une action du workflow échoue, les modifications SQL doivent être rollbackées.

## Fichier Disque

- Supprimer le fichier indiqué par `collection_file_path` lorsqu'il est présent.
- Si le fichier n'existe pas, ne pas échouer et écrire un warning.
- Si une autre erreur disque survient, retourner `500` et rollbacker la
  transaction SQL.

## Architecture Attendue

Respecter les couches existantes :

- réutiliser `backend/services/users/user_collection_import_service.py` pour
  porter l'orchestration métier de réinitialisation ;
- réutiliser `backend/services/database/user_collection_import_repository.py`
  pour porter la transaction SQL de réinitialisation ;
- étendre les repositories SQL existants sous `backend/services/database/`
  uniquement pour les opérations atomiques nécessaires ;
- contrôleur limité au mapping HTTP ;
- tests backend unitaires ou route tests selon le niveau touché.

Ne pas créer de nouveau service backend ni de nouveau repository orchestrateur
pour cette fonctionnalité.

## Tests Backend

Ajouter ou modifier les tests couvrant :

- suppression des lignes `t_user_collection` ;
- nettoyage de `collection_file_path` ;
- nettoyage de `collection_file_description` ;
- `404` quand aucun fichier de collection ni aucune ligne collection n'existe ;
- réinitialisation acceptée quand seules des lignes `t_user_collection`
  existent ;
- fichier absent sur disque accepté avec warning ;
- erreur de suppression fichier rollbackant la transaction SQL ;
- erreur SQL rollbackant la transaction.

## Contraintes

- Ne pas supprimer les plateformes, studios ou jeux du référentiel global.
- Ne pas changer le schéma de base.
- Ne pas introduire de migration Alembic.
- Ne pas hardcoder de chemin spécifique à un environnement.
