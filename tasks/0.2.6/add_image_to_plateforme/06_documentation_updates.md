# 06 - Documentation fonctionnelle et technique

## Objectif

Mettre à jour la documentation concernée par les images de plateformes.

Cette tâche dépend de :

- `01_database_schema_and_configuration.md`
- `02_backend_user_upload_and_public_images.md`
- `03_backend_admin_moderation_endpoints.md`
- `04_frontend_platform_detail_images.md`
- `05_frontend_admin_image_moderation.md`

## Documents À Mettre À Jour

- `documentation/backend-api.md`
- `documentation/authentication.md`
- `documentation/database.md`
- `documentation/site-plan.md`
- `documentation/frontend-arch.md`
- `documentation/backend-arch.md`
- `README.md`

## Contenu Minimal Attendu

Documenter :

- les nouveaux endpoints backend ;
- les statuts HTTP ;
- les routes publiques ajoutées pour les images `ACCEPTED` ;
- la règle d'authentification de l'upload utilisateur ;
- la règle `ADMIN` pour la modération ;
- la table `t_platform_image` ;
- les enums et contraintes associées ;
- les variables `BACKEND_IMG_DIR` et `PLATFORM_IMAGE_MAX_UPLOAD_BYTES` ;
- le volume Docker ;
- le comportement frontend du détail plateforme ;
- la section admin de Configuration.

## Gouvernance

Si une règle existante est contredite ou affaiblie, demander confirmation avant
modification.

Ne documenter que le comportement réellement implémenté.

## Critères D'Acceptation

- Tous les documents concernés sont vérifiés.
- Les documents modifiés correspondent au comportement implémenté.
- `README.md` mentionne les nouvelles variables et volumes visibles pour les
  mainteneurs.
