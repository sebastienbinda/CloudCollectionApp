# 00 - Analyse existante et contrat fonctionnel

## Objectif

Analyser le code existant lié à l'import, au statut de collection, à la page
Configuration et à la navigation d'onboarding avant de modifier le code.

Cette tâche doit produire un fichier
`00_existing_code_analysis_result.md` dans le dossier
`tasks/0.2.0/reinit_collection/`.

## Points À Lire

- `tasks/0.2.0/reinit_collection/reinit_collection.md`
- `documentation/import.md`
- `documentation/backend-api.md`
- `documentation/backend-arch.md`
- `documentation/database.md`
- `documentation/frontend-arch.md`
- `documentation/site-plan.md`
- `documentation/authentication.md`
- `frontend/src/components/ConfigurationView.jsx`
- `frontend/src/services/UserCollectionApi.js`
- `frontend/src/hooks/collection/useUserCollectionOnboarding.js`
- `backend/controllers/user_collection_import_controller.py`
- `backend/services/users/user_collection_import_service.py`
- `backend/services/database/user_collection_import_repository.py`

## Contrat À Confirmer Dans Le Rapport

Le rapport doit confirmer :

- le endpoint cible est `POST /api/users/collection/reinit` ;
- le endpoint est réservé au profil `USER` ;
- l'utilisateur est toujours dérivé du Bearer token ;
- `200` retourne `{"reinitialized": true}` ;
- `404` retourne `{"error": "Collection introuvable."}` ;
- `404` s'applique quand `collection_file_path` est `NULL` et qu'il n'existe
  aucune entrée dans `t_user_collection` pour l'utilisateur ;
- `500` retourne `{"error": "Unable to reinitialize collection."}` ;
- le fichier absent sur disque déclenche un warning mais pas une erreur.

## Résultat Attendu

Le rapport doit lister :

- les fichiers à modifier ;
- les classes ou hooks à étendre ;
- les tests backend à ajouter ou modifier ;
- les validations frontend à lancer ;
- les documentations concernées.

## Contraintes

- Ne pas modifier le comportement applicatif dans cette tâche.
- Ne pas créer de nouveau framework ou dépendance.
- Ne pas modifier de documentation fonctionnelle autre que le rapport d'analyse.
