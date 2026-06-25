# Documentation du partage de collection

## Objectif

Documenter le comportement final validé du partage de collection et enregistrer
les règles de gouvernance associées.

## Dépendance

- Sous-tâches 01 à 08 terminées et comportement final validé.

## Périmètre

- Créer `documentation/share.md` avec une synthèse concise destinée aux agents
  IA : cycle de vie, permissions, sécurité, révocation, code `411`, routes et
  comportements frontend.
- Mettre à jour `documentation/users.md` pour le profil `GUEST` et son absence
  d'héritage de droits USER ou ADMIN.
- Mettre à jour `documentation/authentication.md` pour les deux tokens, les
  claims GUEST, l'échange, la validation en base et la révocation.
- Mettre à jour `documentation/backend-api.md` avec les endpoints, payloads,
  statuts et règles de masquage.
- Mettre à jour `documentation/database.md` avec la table de partage et ses
  règles de conservation.
- Mettre à jour `documentation/collection.md` avec la résolution du propriétaire
  et les permissions de consultation.
- Mettre à jour `documentation/frontend-arch.md`, `documentation/site-plan.md`
  et `documentation/menu.md` avec la route d'échange, l'écran propriétaire et
  les vues GUEST.
- Ajouter `documentation/share.md` dans les règles de documentation fonctionnelle
  et de Change Governance de `AGENTS.md`.
- Mettre à jour `README.md` pour la fonctionnalité utilisateur visible et toute
  configuration réellement ajoutée.
- Fournir le rapport de conformité documentaire avec un statut par document
  concerné.

## Hors périmètre

- Modification du comportement applicatif.
- Ajout d'une route, migration ou composant oublié dans les tâches précédentes.

## Critères d'acceptation

- La documentation décrit le comportement réellement livré sans contradiction.
- `documentation/share.md` est référencé par `AGENTS.md`.
- Les profils, routes, statuts HTTP et permissions concordent dans tous les
  documents.
- README et rapport de conformité sont à jour.
