# Écran de gestion des partages

## Objectif

Ajouter l'écran propriétaire permettant de créer, consulter, copier et révoquer
les liens de partage.

## Dépendances

- Sous-tâches 03 et 05 terminées.

## Périmètre

- Lire `documentation/frontend-arch.md`, `documentation/site-plan.md` et
  `documentation/menu.md`.
- Ajouter un encart dans Configuration pour les utilisateurs USER propriétaires
  d'une collection.
- Ajouter une page routée dédiée utilisant `PageLayout`.
- Créer un service API et un hook de domaine dédiés à la gestion des partages.
- Fournir un formulaire avec durée de 1 à 240 heures et les trois permissions.
- Empêcher côté interface la soumission sans accès collection ni wishlist, tout
  en conservant la validation backend.
- Afficher les partages avec date de création, expiration, permissions, statut,
  copie du lien et action de révocation.
- Demander confirmation avant révocation.
- Afficher les partages expirés avec un encart rouge et conserver les partages
  révoqués visibles.
- Prévoir un rendu desktop et une présentation mobile dédiée.
- Ne jamais afficher cet encart ni cette page aux profils GUEST ou ADMIN.

## Hors périmètre

- Rendu des pages collection pour un invité.
- Modification des règles backend de partage.

## Tests et validations attendus

- États chargement, erreur et liste vide.
- Validation des bornes de durée et des permissions.
- Création, copie presse-papiers et révocation.
- Rendus actif, expiré et révoqué.
- Build frontend réussi.

## Critères d'acceptation

- Toutes les décisions métier restent dans le backend ou le hook de domaine.
- La page respecte `PageLayout`, l'architecture frontend et les contraintes
  desktop/mobile.
