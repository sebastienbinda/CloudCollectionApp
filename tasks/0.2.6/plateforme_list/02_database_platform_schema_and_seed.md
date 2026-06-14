# 02 - Schéma SQL plateformes et chargement initial

## Objectif

Adapter `t_platform` au nouveau modèle de référentiel applicatif et charger les
plateformes fournies par le CSV.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.6/plateforme_list/00_existing_code_analysis_result.md`
- `tasks/0.2.6/plateforme_list/01_platform_catalog_csv_and_contract.md`
- `tasks/0.2.6/plateforme_list/01_platform_catalog_csv_contract_result.md`
- `documentation/database.md`

## Backend À Modifier

Selon les noms confirmés dans le rapport d'analyse :

- modèle ORM `Platform` ;
- migration Alembic ;
- éventuel service de seed / bootstrap du catalogue plateformes ;
- repository plateforme ;
- tests de migration, modèle ou repository.

## Règles De Migration

- Ajouter `end_date` à `t_platform`.
- Supprimer ou conserver `status` uniquement selon la décision du rapport
  d'analyse.
- Mettre à jour la nullabilité de `release_date` et `manufacturer` selon le
  contrat retenu pour les valeurs inconnues du CSV.
- Charger les plateformes du CSV selon la stratégie validée en analyse.
- Ne pas modifier une migration déjà publiée.
- Ne pas supprimer de données existantes sans confirmation explicite si cela
  contredit `documentation/database.md`.

## Tests Attendus

Ajouter ou modifier des tests backend couvrant :

- la présence des colonnes attendues ;
- l'absence des colonnes supprimées si applicable ;
- le parsing et l'insertion des dates connues ;
- la conversion de `Inconnue` en `NULL` ;
- le comportement idempotent du chargement si retenu ;
- la non-création de doublons de plateformes.

## Critères D'Acceptation

- La migration Alembic est créée.
- Le modèle ORM reflète le schéma cible.
- Le catalogue plateformes est disponible dans une base vide après migration ou
  démarrage selon l'architecture retenue.
- Les tests backend ciblés passent.
