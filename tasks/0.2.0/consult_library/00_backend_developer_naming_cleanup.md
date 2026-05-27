# 00 - Correction du nommage developer backend

## Objectif

Corriger l'existant pour utiliser partout l'orthographe anglaise correcte
`developer` au lieu de `developper`.

Cette tâche est un prérequis avant de développer les endpoints Bibliothèque qui
exposent les développeurs de jeux.

## Étapes

1. Vérifier si la migration initiale contenant `t_game.developper` est déjà
   présente dans une release publiée.
2. Si la migration initiale est publiée, créer une nouvelle migration Alembic
   corrective qui renomme la colonne `t_game.developper` en
   `t_game.developer`.
3. Si la migration initiale n'est pas publiée, corriger la migration initiale
   selon les règles de `documentation/database.md`.
4. Corriger le modèle ORM `Game` pour exposer `developer`.
5. Corriger les repositories qui lisent ou écrivent cette colonne.
6. Corriger les tests backend impactés.
7. Corriger `documentation/database.md`.
8. Corriger les rapports ou documents de tâche qui mentionnent encore
   `developper`.

## Critères d'acceptation

- Le code source backend n'utilise plus `developper`.
- Le contrat base documenté utilise `developer`.
- Les migrations respectent les règles d'immutabilité des migrations publiées.
- Les données existantes sont conservées lors du renommage.
- Les endpoints et futurs contrats API utilisent uniquement `developer`.

## Validation attendue

- Lancer les tests backend ciblés.
- Lancer `./test_backend.sh`.
- Vérifier `git diff --check`.
- Rebuilder l'image Docker backend si le comportement runtime ou les migrations
  changent.
