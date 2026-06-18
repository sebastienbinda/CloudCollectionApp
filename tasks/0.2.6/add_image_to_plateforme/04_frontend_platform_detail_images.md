# 04 - Frontend détail plateforme, affichage et upload

## Objectif

Mettre à jour la page de détail public d'une plateforme pour afficher les images
acceptées et permettre l'upload aux utilisateurs connectés.

Cette tâche dépend de :

- `00_existing_code_analysis_result.md`
- `02_backend_user_upload_and_public_images.md`
- `documentation/frontend-arch.md`
- `documentation/site-plan.md`
- `documentation/authentication.md`

## Frontend À Modifier

Selon les noms confirmés dans le rapport d'analyse :

- service API Bibliothèque ;
- hook de détail plateforme ;
- composant de détail plateforme ;
- styles associés.

## Règles UI

- La page reste publique.
- Le bouton d'ajout d'image est visible uniquement pour un utilisateur connecté.
- L'upload utilise le champ multipart `image`.
- Les erreurs backend sont affichées clairement.
- Les images `ACCEPTED` retournées par le détail plateforme sont affichées.
- L'image `MAIN` est mise en avant.
- S'il n'y a pas de `MAIN`, la première image `OTHER` est utilisée comme image
  mise en avant.
- Les autres images sont affichées dans un diaporama limité à 5 images.
- S'il n'y a pas d'image, aucun bloc image ni diaporama n'est affiché.
- Les URLs d'image utilisent le cache-busting prévu par le backend/frontend.

## Contraintes Architecture

- Garder les appels HTTP dans `frontend/src/services/`.
- Garder l'orchestration d'état dans les hooks de domaine.
- Le composant de page reste concentré sur le rendu et les interactions.
- Ne pas rendre la page privée.

## Tests Et Validation Attendus

Ajouter ou modifier les tests disponibles si le projet en contient pour cette
zone.

Valider au minimum :

- build frontend ;
- affichage sans image ;
- affichage avec image `MAIN` ;
- affichage avec seulement des images `OTHER` ;
- bouton upload visible connecté et absent non connecté ;
- gestion d'erreur upload.

## Critères D'Acceptation

- La page détail plateforme respecte `documentation/site-plan.md`.
- L'upload fonctionne depuis le frontend.
- L'affichage est responsive.
- Les validations frontend disponibles passent.
