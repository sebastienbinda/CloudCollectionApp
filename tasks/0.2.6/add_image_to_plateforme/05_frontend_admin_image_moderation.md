# 05 - Frontend Configuration, modération des images

## Objectif

Ajouter dans Configuration une section réservée aux administrateurs pour lister,
visualiser, accepter, refuser et définir l'image principale d'une plateforme.

Cette tâche dépend de :

- `00_existing_code_analysis_result.md`
- `03_backend_admin_moderation_endpoints.md`
- `documentation/frontend-arch.md`
- `documentation/site-plan.md`
- `documentation/menu.md`

## Frontend À Modifier

Selon les noms confirmés dans le rapport d'analyse :

- service API admin Bibliothèque ou service dédié aux images ;
- hook de modération des images ;
- page `ConfigurationView` ou sous-composant dédié ;
- styles associés.

## Règles UI

- La section est visible uniquement pour un profil `ADMIN`.
- L'accès doit aussi dépendre de la découverte des routes backend quand le
  pattern existant le permet.
- La liste est paginée en réutilisant le composant tableau commun.
- Les filtres `status` et `platform` sont des listes de sélection.
- Le tableau affiche :
  - nom de la plateforme ;
  - statut ;
  - type ;
  - miniature ;
  - `user_id` enregistré lors de l'upload ;
  - utilisateur proposant l'image ;
  - date de création ;
  - actions disponibles.
- La miniature est l'image originale redimensionnée côté frontend.
- Un clic sur la miniature permet de voir l'image en plus grand.
- L'acceptation appelle l'endpoint de statut.
- Le refus appelle l'endpoint de statut et supprime l'image de la liste locale
  après succès.
- La définition `MAIN` appelle l'endpoint de type et rafraîchit la liste.

## Tests Et Validation Attendus

Ajouter ou modifier les tests disponibles si le projet en contient pour cette
zone.

Valider au minimum :

- section absente pour non-admin ;
- section visible pour admin autorisé ;
- filtres et pagination ;
- actions accepter, refuser et définir `MAIN` ;
- messages d'erreur et de succès ;
- build frontend.

## Critères D'Acceptation

- L'écran respecte l'architecture frontend.
- Les actions admin utilisent les endpoints protégés.
- Les validations frontend disponibles passent.
