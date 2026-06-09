# 03 - Données et tableau wishlist

## Objectif

Implémenter la page `/wishlist` avec chargement des jeux `wishlist=true` et
affichage du tableau attendu.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.0/user_wishlist_view/00_existing_code_analysis_result.md`
- `tasks/0.2.0/user_wishlist_view/02_frontend_shared_collection_components.md`
- `tasks/0.2.0/user_wishlist_view/user_wishlist_view.md`

## Chargement Des Données

Utiliser l'endpoint existant :

```http
GET /collections/videogames/games/search?wishlist=true
```

Le frontend doit :

- réutiliser le service de consultation collection existant ;
- modifier `VideoGamesApi.fetchGames` pour qu'il accepte des critères de
  recherche et soit utilisable par la page plateforme et par la page wishlist ;
- conserver la normalisation des champs utiles au tableau ;
- ne pas créer de route backend dédiée ;
- ne pas appeler les anciennes routes wishlist supprimées.

## Rendu Attendu

La page wishlist affiche uniquement les colonnes :

- `Nom du jeu`
- `Plateforme`
- `Studio`
- `Date de sortie`
- `Version`

La page wishlist :

- n'affiche pas de sélecteur de plateforme ;
- n'affiche pas d'action de ligne ;
- n'affiche pas les champs d'achat, prix, note ou identifiants techniques ;
- n'affiche pas le champ technique `wishlist` ;
- affiche `Plateforme` comme texte simple non cliquable ;
- gère un état vide quand aucun jeu wishlist n'existe ;
- gère un état de chargement ;
- gère un message d'erreur en cas d'échec de chargement.

## Filtres Et Tris

La page wishlist doit :

- proposer un filtre sur `Plateforme` ;
- demander le tri backend par `name` ;
- demander le tri backend par `platform_name` ;
- demander le tri backend par `studio_name` ;
- demander le tri backend par `release_date` ;
- demander par défaut `sort=name,asc`.

## Critères D'Acceptation

- `/wishlist` charge uniquement les jeux dont `wishlist=true`.
- La page collection existante continue à demander `wishlist=false`.
- La page plateforme existante continue à demander `wishlist=false` avec son
  `platform_id`.
- Les colonnes visibles correspondent exactement au périmètre attendu.
- Le filtre `Plateforme` fonctionne sur les données chargées.
- Les tris attendus fonctionnent via les paramètres `sort` envoyés au backend.
- La page ne propose aucune action métier.

## Validation Attendue

- Lancer `npm run build` depuis `frontend/`.
- Vérifier manuellement, si un serveur local est disponible :
  - utilisateur avec wishlist ;
  - utilisateur sans wishlist ;
  - filtre par plateforme ;
  - tri par nom ;
  - tri par plateforme ;
  - tri par studio ;
  - tri par date de sortie.
