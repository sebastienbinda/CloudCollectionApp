# 01 - Statut de validation en base de données

## Objectif

Ajouter le statut de validation des jeux dans la structure SQL et dans le modèle
ORM `Game`.

Cette tâche dépend de `00_existing_code_analysis_and_architecture.md`.

## Périmètre

Modifier uniquement la couche base de données et les tests associés :

- migration Alembic ;
- modèle ORM `Game` ;
- repository si nécessaire pour exposer le champ dans les lectures existantes ;
- tests de migration, modèle ou schéma.

## Règles Fonctionnelles

- Ajouter `t_game.status`.
- Les valeurs autorisées sont `WAITING_VALIDATION` et `ACCEPTED`.
- Les jeux existants au moment de la migration doivent être initialisés à
  `ACCEPTED`.
- Le champ doit être non nullable.
- Une contrainte SQL doit empêcher toute autre valeur.

## Contraintes Techniques

- Respecter `documentation/database.md`.
- Utiliser Alembic pour la migration.
- Garder un seul modèle ORM par fichier.
- Ne pas modifier la logique d'import ou de consultation dans cette tâche, sauf
  adaptation minimale nécessaire à la compilation/tests.

## Tests Attendus

Ajouter ou mettre à jour les tests backend couvrant :

- la présence du champ ;
- la contrainte de valeurs ;
- la valeur par défaut des lignes existantes lors de migration ;
- la compatibilité du modèle ORM.

## Critères D'Acceptation

- La migration ajoute et retire correctement le champ au downgrade.
- `Game` expose le statut.
- Les tests backend ciblés passent.
- Aucun comportement frontend n'est modifié.
