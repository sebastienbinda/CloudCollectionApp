# 02 - Contrat de requête Bibliothèque backend

## Objectif

Créer les objets ou utilitaires backend nécessaires pour gérer de façon cohérente la pagination, la recherche par nom et le tri des endpoints Bibliothèque.

## Étapes

1. Définir les valeurs par défaut de pagination :
   - `page=0` ;
   - `size=500`.
2. Appliquer `size=500` lorsque `size` est absent, invalide, négatif ou supérieur à 500.
3. Appliquer `page=0` lorsque `page` est absent, invalide ou négatif.
4. Normaliser le filtre `name` pour une recherche contains sans casse et sans accents.
5. Gérer un ou plusieurs paramètres `sort`.
6. Appliquer `asc` lorsque le sens de tri est absent ou invalide.
7. Revenir au tri `name,asc` lorsque la colonne demandée n'est pas autorisée.
8. Définir les colonnes de tri autorisées par endpoint selon `consult.md` :
   - `platforms` : `name`, `release_date`, `manufacturer` ;
   - `studios` : `name`, `country`, `creation_date` ;
   - `games` : `name`, `release_date`, `developer`, `platform`.
9. Vérifier que le backend utilise déjà `developer` partout grâce à
   `tasks/consult_library/00_backend_developer_naming_cleanup.md`.
10. Ajouter ou mettre à jour les tests unitaires backend du parsing de requête.

## Critères d'acceptation

- Les règles de pagination sont centralisées ou réutilisables.
- Les règles de tri sont sécurisées par une allowlist de colonnes.
- Aucun nom de colonne brut non autorisé n'est injecté dans une requête SQL.
- Les comportements invalides retombent sur les valeurs par défaut sans erreur.

## Validation attendue

- Lancer les tests backend ciblés.
- Lancer la suite backend complète si les utilitaires sont partagés.
