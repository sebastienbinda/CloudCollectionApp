# 00 - Rapport d'analyse du code existant et architecture proposée

## Synthèse

La page wishlist peut être ajoutée sans modification backend. Le contrat
existant `GET /collections/videogames/games/search` accepte déjà le filtre
`wishlist=true` et retourne les champs nécessaires au tableau, dont
`platform_name`.

L'implémentation doit rester frontend et documentation uniquement. La meilleure
approche consiste à extraire le noyau de consultation de jeux actuellement
enfermé dans la page plateforme, puis à le piloter par configuration pour
servir deux vues :

- la page plateforme existante, filtrée par `platform_id` et `wishlist=false` ;
- la nouvelle page `/wishlist`, globale, filtrée par `wishlist=true`.

## Documentation Consultée

- `documentation/collection.md`
- `documentation/frontend-arch.md`
- `documentation/site-plan.md`
- `documentation/menu.md`
- `documentation/backend-api.md`
- `tasks/0.2.0/user_wishlist_view/user_wishlist_view.md`

## Cartographie Du Code Existant

### Routes Et Navigation

- `frontend/src/appRouting.js`
  - `AppRouting.isPublicPath(pathname)` liste les routes publiques. `/wishlist`
    ne devra pas y être ajouté.
  - `AppRouting.getViewFromUrl()` mappe les chemins vers les vues React. Il
    faudra ajouter `/wishlist` vers une vue `wishlist`.
  - La page plateforme est actuellement déduite par la présence de
    `platform_id` dans l'URL.

- `frontend/src/hooks/navigation/useAppNavigation.js`
  - `currentView` porte la vue active.
  - `openView(view, path)` centralise la navigation simple.
  - `goHome()` ouvre `/collection` uniquement si `canUseCollectionViews` est
    vrai, sinon redirige vers `/configuration`.
  - `openPlatform(platform)` ouvre la page plateforme avec `platform_id`.
  - `handlePopState()` contient le mapping des chemins connus.
  - L'effet `collectionViews` redirige les vues de collection quand
    `canUseCollectionViews` est faux.

- `frontend/src/hooks/app/useCloudCollectionViewModel.js`
  - Calcule `canUseCollectionViews` avec
    `session.hasAccessToken && session.authenticatedProfile !== "ADMIN"`.
  - Compose les hooks de domaine et expose les props consommées par
    `AppViewSwitch`.
  - Instancie actuellement `useGameCollectionPage()` une seule fois pour la
    page plateforme.

- `frontend/src/components/AppViewSwitch.jsx`
  - `buildPageLayoutProps(props)` prépare les props communes des pages.
  - `render(props)` route les vues `home`, `about`, `addGame`, `auth`,
    `configuration`, `users`, `collectionOnboarding`, `library*` et retombe sur
    `renderPlatform(props)`.
  - Il faudra ajouter un rendu explicite `renderWishlist(props)`.

### Menu Principal

- `frontend/src/components/PageLayout.jsx`
  - Monte `MainMenu` et lui transmet les callbacks de navigation.
  - Il faudra ajouter `onOpenWishlist` dans les props de layout.

- `frontend/src/components/MainMenu.jsx`
  - Rend les boutons `A propos`, `Bibliotheque`, `Configuration`,
    `Ma collection`, `Connexion` et `Deconnexion`.
  - Utilise `isAuthenticated` et `canUseCollectionViews`.
  - Les entrées inaccessibles doivent rester des boutons `disabled` selon
    `documentation/menu.md`.

### Consultation De Jeux

- `frontend/src/hooks/games/useGameCollectionPage.js`
  - Charge les jeux d'une plateforme via `VideoGamesApi.fetchGames`.
  - Exige `options.selectedPlatform`, ce qui n'est pas compatible avec une
    wishlist globale.
  - Construit `valuesByColumn`, `columnFilters`, `sortConfig`, `columns`,
    `filteredGames`, `sortedGames` et `studioCount`.
  - Définit actuellement `filterableColumns` à
    `Studio`, `Version`, `Date de sortie`, `Date d'achat`.
  - Masque `id` et `platform_id`.
  - Ajoute les mutations via `usePlatformGameMutations`, utiles à la page
    plateforme mais interdites sur la wishlist.

- `frontend/src/components/PlatformDetailView.jsx`
  - Rend le `PageLayout`, les statistiques plateforme, le sélecteur
    plateforme, les messages, `ProgressBar`, `TableComponent` et
    `EditGameDialog`.
  - Contient la logique de rendu des actions `Modifier` et `Supprimer`.
  - Contient `isTopRatedGame`, spécifique à l'affichage de la colonne `Note`,
    qui ne concerne pas la wishlist.

- `frontend/src/components/TableComponent.jsx`
  - Est déjà un tableau réutilisable avec filtres par colonne, tri, actions de
    ligne optionnelles, labels de colonnes et pagination optionnelle.
  - Supporte `sortableColumns` pour limiter les tris.
  - Rend une ligne de filtres dès que `onColumnFiltersChange` ou
    `renderColumnFilter` est fourni.
  - Le filtre par défaut est dérivé du type de colonne via
    `collectionUtils.isSelectFilterColumn`.

- `frontend/src/collectionUtils.js`
  - Contient `filterGames(games, columns, columnFilters)`.
  - Contient `sortGames(games, sortConfig)`.
  - `sortGames` est actuellement utilisé par la page plateforme, mais cette
    approche doit être remplacée pour les listes issues du backend.
  - `isSelectFilterColumn(column)` retourne `true` pour les colonnes studio ou
    développeur, et pour `Version`; il ne couvre pas `Plateforme`.
  - `getColumnClassName(column)` couvre `Nom du jeu`, les dates, `Note`,
    `Version` et `Prix d'achat`; `Plateforme` n'a pas de classe dédiée.

### API Frontend

- `frontend/src/services/VideoGamesApi.js`
  - `fetchGames(platformId)` appelle
    `/collections/videogames/games/search?platform_id=<id>&wishlist=false`.
  - `fetchGames` doit être rendu paramétrable pour couvrir la page plateforme
    et la page wishlist.
  - `fetchPlatforms()` et `fetchHomeStats()` demandent déjà
    `wishlist=false`.
  - `searchGamesByName(query)` demande déjà `wishlist=false`.
  - `normalizeCollectionGames(games)` produit déjà les colonnes nécessaires :
    `Nom du jeu`, `Plateforme`, `Studio`, `Date de sortie`, `Version`, ainsi
    que d'autres champs inutiles pour la wishlist.
  - `buildCollectionGameSearchQuery(criteria)` peut déjà encoder
    `wishlist=true`.

### Styles Réutilisables

- `frontend/src/styles.css`
  - Contient les styles généraux `controls`, `tableWrapper`,
    `secondaryButton`.
- `frontend/src/styles/home.css`
  - Contient les styles du menu principal et des boutons de menu.
- `frontend/src/styles/editorial-views.css`
  - Contient les styles `platformDetailStats` et `topRatedGameRow`.

La page wishlist peut réutiliser les styles existants de `PageLayout`,
`TableComponent`, `ProgressBar`, messages `.error` et structure `.container`.
Il n'y a pas besoin d'une nouvelle charte visuelle.

## Contrats Existants Confirmés

- Le backend expose déjà `wishlist=true` et `wishlist=false` sur
  `GET /collections/videogames/games/search`.
- Le backend expose déjà le tri `sort` pour les jeux via
  `UserCollectionQueryParser` et `SqlAlchemyUserCollectionQueryRepository`.
  Les colonnes nécessaires à la wishlist (`name`, `platform_name`,
  `studio_name`, `release_date`) sont déjà autorisées.
- Aucun nouveau endpoint backend n'est nécessaire.
- La page `Ma collection`, la liste des plateformes et la recherche d'accueil
  doivent continuer à envoyer `wishlist=false`.
- La page `/wishlist` doit envoyer `wishlist=true`.
- Le champ technique `wishlist` retourné par l'API ne doit pas être affiché.
- La colonne `Plateforme` doit être affichée comme texte simple non cliquable.
- La page wishlist ne doit pas afficher de sélecteur de plateforme.
- La page wishlist ne doit pas afficher d'actions de ligne.
- Les données de collection et wishlist restent celles de l'utilisateur
  connecté, déduit du Bearer token.
- Les tris des listes persistées doivent être demandés au backend via `sort`.
  Le frontend ne doit pas recalculer l'ordre des listes de jeux collection ou
  wishlist après chargement.

## Décisions De Contrat

- L'entrée `Liste de souhaits` doit être visible mais désactivée quand elle est
  inaccessible. La formulation de la tâche chapeau "cachée (disabled)" est
  interprétée comme `disabled`, car `documentation/menu.md` impose de
  désactiver plutôt que masquer les entrées indisponibles.
- L'entrée `Liste de souhaits` suit l'ordre de navigation documenté. Elle doit
  être placée avec les entrées de navigation avant l'action de session finale.
  Avec les libellés actuels, l'ordre cible connecté est :
  `A propos`, `Bibliotheque`, `Configuration`, `Liste de souhaits`,
  `Ma collection`, puis `Deconnexion`.
- `/wishlist` est une route privée de collection. Elle doit suivre les mêmes
  restrictions frontend que `Ma collection`.
- Le profil `ADMIN` ne doit pas accéder à `/wishlist`, car
  `documentation/site-plan.md` interdit les écrans de collection ownership à ce
  profil. Une ouverture directe de `/wishlist` doit rediriger vers
  `/configuration` pour `ADMIN`.
- Les filtres de colonne affichés restent gérés côté frontend pour cette
  évolution, mais les tris doivent être demandés au backend avec le paramètre
  `sort`. La page plateforme doit aussi être alignée sur cette règle.
- Le filtre `Plateforme` doit être le seul filtre visible sur la wishlist.
  Les autres colonnes restent triables selon la tâche, mais ne doivent pas
  afficher de contrôles de filtre.
- `VideoGamesApi.fetchGames` doit devenir la méthode unique de chargement des
  jeux de collection/wishlist. Aucune méthode `fetchWishlistGames` ne doit être
  créée.

## Architecture Cible Proposée

### Navigation Et Menu

Modifier `frontend/src/appRouting.js` :

- ajouter `/wishlist` dans `AppRouting.getViewFromUrl()` avec la vue
  `wishlist` après le contrôle de session ;
- ne pas ajouter `/wishlist` à `AppRouting.isPublicPath()`.

Modifier `frontend/src/hooks/navigation/useAppNavigation.js` :

- ajouter `/wishlist: "wishlist"` dans le mapping `handlePopState()`;
- ajouter `wishlist` à la liste `collectionViews` utilisée par la redirection
  quand `canUseCollectionViews` est faux ;
- ajouter une callback `openWishlist()` qui ouvre `wishlist` sur `/wishlist`
  si `canUseCollectionViews` est vrai, sinon ouvre `/configuration`.

Modifier `frontend/src/hooks/app/useCloudCollectionViewModel.js` :

- exposer `openWishlist: navigation.openWishlist` dans `viewProps`;
- instancier l'état de wishlist selon l'architecture retenue dans la section
  suivante.

Modifier `frontend/src/components/AppViewSwitch.jsx` :

- importer `WishlistView`;
- ajouter `onOpenWishlist` dans `buildPageLayoutProps(props)`;
- ajouter une branche `currentView === "wishlist"` ;
- ajouter `renderWishlist(props)`.

Modifier `frontend/src/components/PageLayout.jsx` :

- accepter `onOpenWishlist`;
- transmettre `onOpenWishlist` à `MainMenu`.

Modifier `frontend/src/components/MainMenu.jsx` :

- accepter `onOpenWishlist`;
- ajouter le bouton `Liste de souhaits`;
- désactiver ce bouton avec `disabled={!isAuthenticated || !canUseCollectionViews}`;
- le placer avant `Ma collection` et avant l'action de session finale.

### Hook De Consultation Partagé

Créer ou extraire un hook :

```text
frontend/src/hooks/games/useCollectionGamesTable.js
```

Responsabilité :

- charger une liste de jeux via `loadGames` ;
- gérer `games`, `valuesByColumn`, `columnFilters`, `sortConfig` et
  `isLoadingGames` ;
- calculer `namedGames`, `columns`, `filteredGames`, `sortedGames` et
  `studioCount` ;
- accepter une configuration explicite : `enabled`, `loadGames`,
  `visibleColumns`, `filterableColumns`, `sortableColumns`,
  `defaultSortConfig`, `sortColumnMapping`, `errorMessage`, `onError` et
  `reloadKey` ;
- demander un nouveau chargement backend quand la configuration de tri change,
  au lieu de trier localement avec `sortGames`.

Modifier `frontend/src/hooks/games/useGameCollectionPage.js` :

- le garder comme hook de page plateforme ;
- le faire déléguer à `useCollectionGamesTable`;
- conserver `usePlatformGameMutations` uniquement ici ;
- configurer :
  - `enabled: hasAccessToken && selectedPlatform`;
  - `loadGames: (criteria) => VideoGamesApi.fetchGames({ platform_id: selectedPlatform, wishlist: false, ...criteria })`;
  - colonnes visibles compatibles avec l'existant ;
  - filtres existants ;
  - tri backend par défaut `sort=name,asc`.

Créer :

```text
frontend/src/hooks/games/useWishlistPage.js
```

Responsabilité :

- déléguer à `useCollectionGamesTable`;
- configurer :
  - `enabled: hasAccessToken && currentView === "wishlist"`;
  - `loadGames: (criteria) => VideoGamesApi.fetchGames({ wishlist: true, ...criteria })`;
  - `visibleColumns: ["Nom du jeu", "Plateforme", "Studio", "Date de sortie", "Version"]`;
  - `filterableColumns: ["Plateforme"]`;
  - `sortableColumns: ["Nom du jeu", "Plateforme", "Studio", "Date de sortie"]`;
  - `sortColumnMapping: { "Nom du jeu": "name", Plateforme: "platform_name", Studio: "studio_name", "Date de sortie": "release_date" }`;
  - `defaultSortConfig: { column: "Nom du jeu", direction: "asc" }`, converti en
    `sort=name,asc` pour l'appel backend ;
  - message d'erreur : `Impossible de charger la liste de souhaits.`;
- ne pas exposer de mutations.

### Service Frontend

Modifier `frontend/src/services/VideoGamesApi.js` :

- modifier la méthode existante :

```js
static async fetchGames(criteria = {})
```

- cette méthode doit construire la query string depuis les critères fournis et
  appeler :

```http
/collections/videogames/games/search?<criteria>
```

- elle doit accepter au minimum `platform_id`, `wishlist` et `sort` ;
- elle doit réutiliser `buildCollectionGameSearchQuery` et
  `normalizeCollectionGames`.

Ne pas créer de méthode `fetchWishlistGames`. Le service doit rester centré sur
un chargement de jeux paramétrable.

### Composants React

Créer :

```text
frontend/src/components/CollectionGamesTable.jsx
```

Responsabilité :

- afficher `ProgressBar` de chargement ;
- afficher l'état vide ;
- afficher `TableComponent` ;
- recevoir les données de tableau, messages, colonnes triables, callbacks de
  tri/filtre, actions optionnelles et classe de ligne optionnelle.

Important : pour que la wishlist affiche uniquement un filtre `Plateforme`,
`CollectionGamesTable` doit permettre de fournir un `renderColumnFilter` qui
retourne `null` pour les colonnes non filtrables. Sinon `TableComponent`
affichera des contrôles de filtre pour toutes les colonnes visibles dès que
`onColumnFiltersChange` est fourni.

Modifier `frontend/src/components/PlatformDetailView.jsx` :

- conserver la page, le `PageLayout`, les statistiques et le sélecteur de
  plateforme ;
- remplacer le bloc `ProgressBar` + état vide + `TableComponent` par
  `CollectionGamesTable` ;
- conserver `EditGameDialog` et les actions de ligne uniquement dans cette
  page ;
- déplacer `isTopRatedGame` hors du JSX si nécessaire, mais le garder spécifique
  à la page plateforme.

Créer :

```text
frontend/src/components/WishlistView.jsx
```

Responsabilité :

- utiliser `PageLayout`;
- afficher un titre `Liste de souhaits` ;
- afficher un sous-titre court orienté consultation ;
- afficher les erreurs éventuelles ;
- afficher `CollectionGamesTable` sans `renderRowActions` ;
- ne pas afficher de sélecteur de plateforme ;
- ne pas afficher de statistiques d'achat, prix moyen ou actions.

## Fichiers À Modifier Ou Créer

À créer :

- `frontend/src/components/CollectionGamesTable.jsx`
- `frontend/src/components/WishlistView.jsx`
- `frontend/src/hooks/games/useCollectionGamesTable.js`
- `frontend/src/hooks/games/useWishlistPage.js`

À modifier :

- `frontend/src/appRouting.js`
- `frontend/src/hooks/navigation/useAppNavigation.js`
- `frontend/src/hooks/app/useCloudCollectionViewModel.js`
- `frontend/src/components/AppViewSwitch.jsx`
- `frontend/src/components/PageLayout.jsx`
- `frontend/src/components/MainMenu.jsx`
- `frontend/src/components/PlatformDetailView.jsx`
- `frontend/src/hooks/games/useGameCollectionPage.js`
- `frontend/src/services/VideoGamesApi.js`
- `frontend/src/collectionUtils.js` uniquement si le filtre `Plateforme` est
  généralisé, même si l'injection locale du filtre reste préférable.

À ajouter comme demande de documentation d'architecture :

- `documentation/frontend-arch.md` : formaliser que les tris de listes backend
  doivent être envoyés au backend et non recalculés côté React.
- `documentation/backend-arch.md` : formaliser que le backend est responsable
  de l'ordre de retour des endpoints exposant un paramètre `sort`.

Documentation à modifier en fin de chantier :

- `documentation/collection.md`, `documentation/site-plan.md` et
  `documentation/menu.md` ;
- `documentation/frontend-arch.md` si le hook ou composant partagé devient un
  nouveau pattern notable ;
- `documentation/backend-api.md` seulement si le filtre wishlist doit être
  clarifié ;
- `README.md` si la route `/wishlist` ou le comportement utilisateur y sont
  documentés.

## Risques Identifiés

- `TableComponent` affiche des filtres pour toutes les colonnes visibles dès
  qu'un filtre est activé. Sans `renderColumnFilter`, la wishlist risque
  d'afficher plus que le filtre `Plateforme`.
- `useGameCollectionPage` mélange chargement, colonnes, filtres et mutations.
  Une extraction trop large peut changer le comportement de la page plateforme.
  La factorisation doit être incrémentale et vérifiée.
- `AppViewSwitch.render()` retombe actuellement sur la page plateforme par
  défaut. Sans branche explicite `wishlist`, une erreur de mapping pourrait
  afficher la mauvaise page.
- Les fichiers `AppViewSwitch.jsx`, `PlatformDetailView.jsx` et
  `useCloudCollectionViewModel.js` sont déjà assez longs. Les nouveaux
  composants/hooks doivent éviter de pousser ces fichiers vers la limite de
  500 lignes.
- Le libellé de la tâche "cachée (disabled)" est contradictoire. La décision
  retenue est `disabled`, car elle respecte la documentation.
- Si `Plateforme` est ajoutée globalement comme colonne à filtre select, cela
  peut modifier d'autres tableaux. Une injection locale est moins risquée.
- Le backend supporte la pagination et le tri. Ajouter une pagination wishlist
  serait hors périmètre, mais le tri backend est requis.

## Critères Pour Les Sous-Tâches Suivantes

- Navigation : ajouter `/wishlist`, `openWishlist`, `currentView === "wishlist"`
  et l'entrée de menu désactivable.
- Composants partagés : extraire le tableau sans changer le comportement visible
  de la page plateforme.
- Wishlist : charger `wishlist=true`, afficher exactement les colonnes prévues
  et limiter les filtres visibles à `Plateforme`.
- Tri backend : remplacer le tri frontend par `sort` pour plateforme et
  wishlist, puis demander l'ajout de cette règle dans
  `documentation/frontend-arch.md` et `documentation/backend-arch.md`.
- La documentation finale doit expliquer que `/wishlist` est une route privée
  de collection, indisponible pour `ADMIN`.

## Écarts Ou Points À Clarifier

- Aucun écart bloquant avec la tâche chapeau.
- La tâche chapeau dit "cachée (disabled)" pour l'entrée menu. La règle projet
  applicable est `disabled` et non masquée.
- La tâche chapeau parle d'un paramètre de configuration `wishlist` pour le
  composant commun. Le rapport propose une configuration plus explicite
  (`visibleColumns`, `filterableColumns`, `sortableColumns`, `sortColumnMapping`,
  `loadGames`) car elle évite d'encoder plusieurs comportements dans un booléen.

## Validations À Exécuter Après Implémentation

- `npm run build` depuis `frontend/`.
- Vérification manuelle si un serveur local est disponible : accès `/wishlist`
  connecté non-`ADMIN`, sans session et avec profil `ADMIN`, entrée menu,
  page plateforme inchangée, page collection inchangée, wishlist vide, wishlist
  avec jeux, filtre `Plateforme`, tris backend `Nom du jeu`, `Plateforme`,
  `Studio`, `Date de sortie`.
- `./test_backend.sh` seulement si une modification backend est finalement
  réalisée, ce qui n'est pas attendu.
- Rebuild Docker frontend si le changement est livré dans l'image web :

```bash
docker compose -f docker/docker-compose.local.yml build web
```

## Conformité Documentaire

🟢 `documentation/collection.md` : concerné, vérifié et respecté. La wishlist
utilise les filtres existants, sans nouveau backend.

🟢 `documentation/frontend-arch.md` : concerné, vérifié et respecté.
L'architecture cible garde les services, hooks et composants dans leurs
responsabilités. Une mise à jour doit être demandée pour formaliser le tri
backend obligatoire.

🟢 `documentation/site-plan.md` : concerné, vérifié et respecté. `/wishlist`
est une route privée de collection et suit l'exclusion `ADMIN`.

🟢 `documentation/menu.md` : concerné, vérifié et respecté. L'entrée
inaccessible est désactivée et non masquée.

🟢 `documentation/backend-api.md` : concerné, vérifié et respecté. Le contrat
`wishlist=true` existe déjà sur l'endpoint de recherche de jeux.

🟢 `documentation/backend-arch.md` : concerné par la nouvelle règle de tri à
formaliser. Une mise à jour doit être demandée avant modification effective.

🟠 `documentation/authentication.md`, `documentation/database.md`,
`documentation/register.md`, `documentation/users.md` et
`documentation/about.md` : non concernés par cette tâche d'analyse.
