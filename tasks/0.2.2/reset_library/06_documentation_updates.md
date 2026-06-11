# Mise à jour de la documentation

## Objectif

Mettre à jour les documents fonctionnels impactés par le reset Bibliotheque.

## Périmètre

- `documentation/backend-api.md` :
  - documenter `POST /api/library/reset` ;
  - documenter `202`, `403`, `409` et erreurs attendues ;
  - documenter les endpoints d'import bloqués pendant reset.
- `documentation/bibliotheque.md` :
  - conserver les routes publiques de consultation en read-only ;
  - ajouter l'exception administrateur protégée pour reset ;
  - documenter la reconstruction partielle possible en cas d'échecs utilisateurs.
- `documentation/import.md` :
  - documenter le refus `403` pendant reset pour les routes d'import.
- `documentation/site-plan.md` :
  - documenter l'encart admin dans Configuration.
- `documentation/database.md` :
  - vérifier si aucune modification de structure n'est nécessaire ;
  - mettre à jour uniquement si les règles de persistance changent.
- `README.md` :
  - vérifier s'il doit être mis à jour pour une variable d'environnement email
    ou un comportement utilisateur visible.

## Critères d'acceptation

- La documentation ne contredit plus le reset administrateur.
- Les routes publiques Bibliotheque restent explicitement publiques en lecture.
- Les changements d'invariant sont assumés et documentés.
