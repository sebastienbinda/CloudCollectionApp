# 04 - Tri backend des listes collection et wishlist

## Objectif

Supprimer le tri frontend des listes de jeux issues du backend et faire passer
tous les tris de consultation collection/wishlist par les paramètres `sort` des
endpoints existants.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.0/user_wishlist_view/00_existing_code_analysis_result.md`
- `tasks/0.2.0/user_wishlist_view/02_frontend_shared_collection_components.md`
- `tasks/0.2.0/user_wishlist_view/03_frontend_wishlist_data_and_table.md`
- `documentation/backend-api.md`

## Règles Attendues

- Le frontend ne doit pas trier localement les listes de jeux chargées depuis
  `GET /collections/videogames/games/search`.
- Le tri demandé par l'utilisateur doit être converti en paramètre backend
  `sort=<colonne>,<direction>`.
- La page plateforme doit continuer à charger les jeux avec
  `wishlist=false` et `platform_id=<id>`.
- La page wishlist doit charger les jeux avec `wishlist=true`.
- Le tri par défaut de la wishlist doit envoyer `sort=name,asc`.
- Le tri par défaut de la page plateforme doit rester cohérent avec l'existant,
  en envoyant `sort=name,asc`.
- Le mapping frontend/backend des colonnes triables doit être explicite :
  - `Nom du jeu` -> `name`
  - `Plateforme` -> `platform_name`
  - `Studio` -> `studio_name`
  - `Date de sortie` -> `release_date`
- Les colonnes non supportées par le backend ne doivent pas déclencher de tri
  backend.

## Service Frontend

Modifier `VideoGamesApi.fetchGames` pour qu'il soit utilisable par les deux
besoins au lieu de créer une méthode dédiée wishlist.

Contrat recommandé :

```js
static async fetchGames(criteria = {})
```

La page plateforme appelle `fetchGames` avec :

```js
{
  platform_id: selectedPlatform,
  wishlist: false,
  sort: "name,asc"
}
```

La page wishlist appelle `fetchGames` avec :

```js
{
  wishlist: true,
  sort: "name,asc"
}
```

## Documentation D'Architecture À Demander

Cette tâche doit proposer une mise à jour documentaire et attendre validation
avant modification effective si la règle n'est pas encore documentée :

- `documentation/frontend-arch.md` : ajouter que les tris des listes paginées ou
  consultées depuis le backend doivent être demandés au backend, pas recalculés
  côté React, sauf exception explicitement documentée.
- `documentation/backend-arch.md` : ajouter que les endpoints de consultation
  exposant un paramètre `sort` sont responsables de l'ordre de retour et que le
  backend reste l'autorité des tris sur données persistées.

## Critères D'Acceptation

- Aucune méthode `fetchWishlistGames` n'est créée dans `VideoGamesApi`.
- `fetchGames` accepte les critères nécessaires aux deux vues.
- La page plateforme envoie un paramètre `sort` backend.
- La page wishlist envoie un paramètre `sort` backend.
- Le tri affiché dans le tableau reflète la configuration demandée au backend.
- Les utilitaires de tri frontend ne sont plus utilisés pour ces listes backend.
- La demande de mise à jour de `frontend-arch.md` et `backend-arch.md` est
  explicitement mentionnée dans le bilan de la tâche.

## Validation Attendue

- Lancer `npm run build` depuis `frontend/`.
- Vérifier manuellement, si un serveur local est disponible :
  - tri plateforme par nom ;
  - tri wishlist par nom ;
  - tri wishlist par plateforme ;
  - tri wishlist par studio ;
  - tri wishlist par date de sortie.
