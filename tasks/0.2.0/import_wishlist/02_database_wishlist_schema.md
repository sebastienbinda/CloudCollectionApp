# 02 - Schéma SQL et persistance wishlist

## Objectif

Ajouter la colonne `wishlist` à `t_user_collection` et adapter la couche ORM /
repository pour persister cette information.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.0/import_wishlist/00_existing_code_analysis_result.md`
- `tasks/0.2.0/import_wishlist/import_wishlist.md`

## Backend À Modifier

Selon les noms confirmés dans le rapport d'analyse :

- modèle ORM `t_user_collection` ;
- migration Alembic ;
- repository d'import utilisateur ;
- repository de consultation collection si nécessaire ;
- tests de repository et de migration.

## Règles De Migration

- Ajouter `t_user_collection.wishlist` en `BOOLEAN`.
- La valeur par défaut fonctionnelle est `false`.
- La migration doit préserver les données existantes.
- Les lignes déjà présentes doivent être backfillées à `false`.
- La colonne doit être non nullable sauf justification contraire dans le rapport
  d'analyse.
- Ne pas modifier une migration déjà publiée.

## Tests Attendus

Ajouter ou modifier des tests backend couvrant :

- la présence de la colonne dans le modèle ;
- la création d'une association utilisateur-jeu avec `wishlist=false` par
  défaut ;
- la création d'une association avec `wishlist=true` ;
- la non-duplication de `(user_id, game_id)` ;
- le comportement de backfill ou d'initialisation selon la stratégie retenue.

## Critères D'Acceptation

- La migration Alembic est créée.
- Le modèle ORM reflète la nouvelle colonne.
- Les repositories peuvent écrire et lire la valeur `wishlist`.
- Les données existantes restent compatibles.
- Les tests backend ciblés passent.
