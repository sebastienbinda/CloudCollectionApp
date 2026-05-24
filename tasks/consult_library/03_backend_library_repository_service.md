# 03 - Repositories et service de consultation Bibliothèque

## Objectif

Ajouter la couche backend de lecture permettant de compter et lister les plateformes, studios et jeux de la base globale.

## Étapes

1. Créer ou étendre les repositories nécessaires pour lire les entités globales.
2. Ajouter le comptage global des entités :
   - plateformes ;
   - studios ;
   - jeux.
3. Ajouter la liste paginée des plateformes avec `total_games`.
4. Ajouter la liste paginée des studios avec :
   - `editor_total_games` ;
   - `developer_total_games`.
5. Ajouter la liste paginée des jeux avec les noms associés :
   - `developer` ;
   - `editor` ;
   - `platform`.
6. Créer un service métier de consultation Bibliothèque si cela respecte mieux l'architecture existante.
7. Ajouter les tests unitaires backend des repositories et du service.

## Critères d'acceptation

- Les données proviennent uniquement des tables globales de référence.
- Aucune donnée utilisateur, collection privée ou chemin de fichier n'est exposé.
- Les listes respectent pagination, recherche et tri.
- Les compteurs sont calculés de façon déterministe.
- Les méthodes publiques ajoutées sont documentées en français.

## Validation attendue

- Lancer les tests backend ciblés.
- Lancer `./test_backend.sh`.
- Vérifier si `documentation/database.md` doit être mise à jour.
