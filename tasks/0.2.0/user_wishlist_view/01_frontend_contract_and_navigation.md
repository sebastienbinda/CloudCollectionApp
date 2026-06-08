# 01 - Contrat frontend, route et navigation

## Objectif

Ajouter le contrat de navigation frontend de la page wishlist sans modifier le
backend.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.0/user_wishlist_view/00_existing_code_analysis_result.md`
- `tasks/0.2.0/user_wishlist_view/user_wishlist_view.md`

## Périmètre

Implémenter uniquement :

- la route frontend `/wishlist` ;
- l'identifiant de vue associé ;
- l'action de navigation vers la wishlist ;
- l'entrée de menu `Liste de souhaits` ;
- la protection d'accès cohérente avec les pages de collection.

## Règles Attendues

- La page `/wishlist` est une route frontend privée.
- Un utilisateur non connecté ne doit pas pouvoir ouvrir la page wishlist.
- L'entrée de menu doit respecter `documentation/menu.md`.
- L'entrée de menu doit être placée de façon cohérente avec les autres entrées
  de navigation.
- L'entrée de menu doit appeler une callback de navigation fournie par le view
  model applicatif.
- Le composant `MainMenu` ne doit pas contenir de logique métier.
- Les routes et la déduction de vue restent centralisées dans l'orchestration
  frontend existante.
- Aucun endpoint backend ne doit être ajouté ou modifié.

## Critères D'Acceptation

- `/wishlist` est reconnu par le routeur frontend.
- Le menu contient une entrée `Liste de souhaits` conforme aux règles
  documentées.
- L'accès sans session suit le comportement des routes privées existantes.
- La navigation vers `/collection` et vers les pages bibliothèque reste
  inchangée.
- Aucun appel backend wishlist dédié n'est créé.

## Validation Attendue

- Lancer `npm run build` depuis `frontend/`.
- Vérifier manuellement, si un serveur local est disponible :
  - menu connecté ;
  - menu non connecté ;
  - accès direct à `/wishlist` ;
  - retour aux routes existantes.
