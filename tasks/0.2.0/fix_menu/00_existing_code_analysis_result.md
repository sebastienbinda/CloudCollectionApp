# 00 - Résultat d'analyse du code existant

## Statut

Analyse réalisée pour la tâche `fix_menu`.

Aucune modification fonctionnelle n'a été réalisée pendant cette tâche.

## Documentation Lue

- `tasks/0.2.0/fix_menu/fix_menu.md`
- `documentation/menu.md`
- `documentation/frontend-arch.md`
- `documentation/site-plan.md`
- `documentation/authentication.md`

## Synthèse

Le menu principal est déjà centralisé dans
`frontend/src/components/MainMenu.jsx`, mais il n'est rendu que par certaines
pages. Le footer est actuellement rendu globalement par
`frontend/src/components/AppFrame.jsx`, qui enveloppe toutes les vues depuis
`frontend/src/App.jsx`.

La future migration doit donc créer un layout commun pour les headers, le menu,
le contenu et le footer sans introduire de double footer. Comme `AppFrame` ne
porte aujourd'hui que le footer autour de la vue active, il devient un doublon
fonctionnel de `PageLayout`. La stratégie cible est de déplacer `AppFooter` dans
`PageLayout`, puis de supprimer `AppFrame`.

Les règles de navigation restent déjà centralisées dans
`frontend/src/components/AppViewSwitch.jsx` et les hooks de navigation. Le
layout ne doit pas reprendre cette responsabilité.

## Pages À Migrer

### Pages routées qui utilisent déjà `MainMenu`

- `frontend/src/components/AboutView.jsx` : page publique `/about`, header
  spécifique avec image et contenu marketing.
- `frontend/src/components/HomeView.jsx` : page privée `/collection`, header
  avec dates de premier et dernier jeu.
- `frontend/src/components/LibraryHomeView.jsx` : page publique
  `/bibliotheque`, header Bibliotheque.
- `frontend/src/components/LibraryEntityListView.jsx` : pages publiques
  `/bibliotheque/plateformes`, `/bibliotheque/studios` et
  `/bibliotheque/jeux`, header Bibliotheque générique.
- `frontend/src/components/UserCollectionOnboardingView.jsx` : page privée
  `/collection/import`, header d'onboarding.

### Pages routées sans `MainMenu`

- `frontend/src/components/AuthView.jsx` : page publique `/auth`, header local
  `authHeader` et bouton retour local.
- `frontend/src/components/AdminDashboardView.jsx` : page privée
  `/admin-dashboard`, header local `addGameHeader` et bouton retour local.
- `frontend/src/components/UsersView.jsx` : page admin `/users`, header local
  `addGameHeader` et bouton retour local.
- `frontend/src/components/AddGameView.jsx` : page privée `/add-game`, header
  local `addGameHeader` et bouton retour local.
- `frontend/src/components/PlatformDetailView.jsx` : page privée de détail
  plateforme, hero `platformDetailHero` et bouton retour local.

### Fichiers non routés à ne pas migrer immédiatement

- `frontend/src/components/WishlistView.jsx` existe mais n'est pas importé par
  `AppViewSwitch` ni routé par `appRouting.js`. Il ne doit pas bloquer la
  migration des pages actives. Si cette vue redevient routée plus tard, elle
  devra utiliser `PageLayout`.
- Les modales et dialogues (`AuthSessionModal`, `EditGameDialog`,
  `EditWishlistDialog`) ne sont pas des pages et ne doivent pas recevoir le
  layout global.

## Props Manquantes Par Page

Les props communes nécessaires au menu sont :

- `isAuthenticated`
- `canUseCollectionViews`
- `authenticatedUsername`
- `authenticatedProfile`
- `onOpenAbout`
- `onOpenHome`
- `onOpenLibrary`
- `onOpenAdminDashboard`
- `onLogout`

`MainMenu` reçoit actuellement parfois `platforms`, `selectedPlatform` et
`onOpenPlatform`, mais ces props ne sont pas utilisées par le composant. Elles
peuvent être supprimées des appels lors de la migration si aucun comportement
nouveau ne les justifie.

### Props déjà disponibles

- `AboutView`, `HomeView`, `LibraryHomeView`, `LibraryEntityListView` et
  `UserCollectionOnboardingView` reçoivent déjà les props nécessaires au menu.
  Elles pourront les transmettre à `PageLayout`.

### Props à ajouter depuis `AppViewSwitch`

- `AuthView` reçoit seulement `isAuthenticated`, `canUseCollectionViews`,
  `onAuthenticated` et `onBack`. Il manque :
  `authenticatedUsername`, `authenticatedProfile`, `onOpenAbout`,
  `onOpenHome`, `onOpenLibrary`, `onOpenAdminDashboard` et `onLogout`.
- `AdminDashboardView` reçoit `username`, `authenticatedProfile`,
  `canUseCollectionViews`, `onBack` et `onBackToLibrary`, mais il manque une
  forme homogène des props de menu :
  `isAuthenticated`, `authenticatedUsername`, `onOpenAbout`, `onOpenHome`,
  `onOpenLibrary`, `onOpenAdminDashboard` et `onLogout`.
- `UsersView` reçoit `authenticatedProfile` et `onBack`, mais il manque toutes
  les props communes de menu.
- `AddGameView` reçoit `onBack`, mais il manque toutes les props communes de
  menu.
- `PlatformDetailView` reçoit `isAuthenticated` et `onBack`, mais il manque :
  `canUseCollectionViews`, `authenticatedUsername`, `authenticatedProfile`,
  `onOpenAbout`, `onOpenHome`, `onOpenLibrary`, `onOpenAdminDashboard` et
  `onLogout`.

## Composants À Créer Ou Modifier

### À créer

- `frontend/src/components/PageLayout.jsx`
  - Doit contenir le header commun.
  - Doit intégrer `MainMenu`.
  - Doit exposer un emplacement pour les informations de page :
    `eyebrow`, `title`, `subtitle`, et contenu de header optionnel.
  - Doit rendre le contenu principal.
  - Doit rendre `AppFooter`.
  - Doit rester un composant de rendu et d'interaction UI, sans logique métier.

### À modifier

- `frontend/src/components/MainMenu.jsx`
  - Remplacer l'entrée `Connexion` en `<a>` par un `<button>`.
  - Mettre `Connexion` ou `Deconnexion` en dernière action visible.
  - Garder les comportements d'ouverture, fermeture, clavier et tactile.
- `frontend/src/components/AppFrame.jsx`
  - À supprimer après migration complète vers `PageLayout`, car sa seule
    responsabilité actuelle est de rendre `AppFooter`.
- `frontend/src/App.jsx`
  - À modifier pour retirer l'import et l'utilisation de `AppFrame`.
  - Doit continuer à rendre la vue active et `AuthSessionModal` au niveau de
    composition applicative.
- `frontend/src/components/AppViewSwitch.jsx`
  - Ajouter les props communes de layout/menu aux pages qui ne les reçoivent pas.
  - Option possible : créer une petite méthode statique interne pour construire
    les props communes et limiter la duplication.
- Pages routées listées plus haut
  - Remplacer les headers locaux par `PageLayout`.
  - Conserver le contenu spécifique existant.
  - Retirer les imports directs de `MainMenu` quand ils deviennent inutiles.

## Styles À Réutiliser Ou Adapter

### Styles de structure existants

- `frontend/src/styles.css`
  - `.appShell` : conteneur large sans carte.
  - `.container` : conteneur carte blanche utilisé par les pages sans menu.
  - `.secondaryButton`, `.backButton`, `.buttonLink` : styles globaux de boutons
    secondaires et retours.
  - `button` : style global bleu.
- `frontend/src/styles/home.css`
  - `.pageHeader` : header commun déjà utilisé par plusieurs pages.
  - `.pageHeaderTopActions` : zone du menu et de l'utilisateur connecté.
  - `.pageHeaderActions` : panneau du menu.
  - `.pageHeaderOptionsMenu`, `.pageHeaderOptionsTrigger`,
    `.pageHeaderOptionsIcon` : déclencheur du menu.
  - `.pageHeaderActions .secondaryButton` : style des actions du menu.
  - `.pageHeaderConnectedUser` et `.pageHeaderConnectedUserADMIN` :
    indicateur utilisateur.
  - `.pageHeaderDateSummary` : contenu additionnel utilisé par `HomeView`.
- `frontend/src/styles/editorial-views.css`
  - `.addGameHeader`, `.authHeader`, `.platformDetailHero` : headers locaux à
    réintégrer dans le modèle commun ou à conserver via contenu optionnel.
- `frontend/src/styles/library.css`
  - `.libraryShell`, `.libraryHeader` : variantes Bibliotheque.
- `frontend/src/styles/collection-onboarding.css`
  - `.collectionOnboardingShell`, `.collectionOnboardingHeader` : variante
    onboarding.

### Palette verte existante

Les couleurs vertes déjà présentes et cohérentes avec l'interface sont :

- `#0f766e` : eyebrow et accents.
- `#047857` : messages de succès.
- `#ecfdf5` : fond clair dans le gradient du header.
- `#dcfce7` et `#166534` : statut admin actif.

Pour homogénéiser les boutons du menu, utiliser une combinaison proche de
`#0f766e` pour le fond principal et une variation plus sombre au hover. Éviter
de modifier le style global de tous les boutons si le besoin reste limité au
menu.

## Risques Identifiés

- Double footer : `AppFrame` rend déjà `AppFooter`. La migration doit déplacer
  `AppFooter` dans `PageLayout`, retirer `AppFrame` de `App.jsx`, puis supprimer
  le fichier `AppFrame.jsx`.
- `/auth` est une route publique. Ajouter le menu sur cette page ne doit pas
  déclencher d'appel protégé ni empêcher la connexion ou la création de compte.
- Les pages admin et privées doivent conserver les règles de redirection et
  d'accès de `documentation/site-plan.md` et `documentation/authentication.md`.
- Le profil `ADMIN` ne doit pas recevoir de navigation active vers les vues de
  collection. `Ma collection` doit rester désactivé via `canUseCollectionViews`.
- Le menu ne doit pas contenir de logique métier : il doit continuer à déclencher
  des callbacks reçus par props.
- Le bouton `Connexion` converti en `<button>` ne pourra plus s'appuyer sur
  `href="/auth"`. Il devra utiliser un callback de navigation vers `/auth`, à
  ajouter proprement dans le flux de props.
- L'ordre demandé par la tâche `fix_menu` place `Connexion` ou `Deconnexion` en
  dernier, alors que `documentation/menu.md` indique aujourd'hui que les entrées
  doivent être en ordre alphabétique. La tâche `09_documentation.md` devra
  aligner cette règle documentaire avec l'implémentation demandée.
- Les pages avec hero spécifique (`AboutView`, `PlatformDetailView`) ont une
  structure visuelle différente. `PageLayout` doit accepter du contenu de header
  optionnel sans imposer une seule composition rigide.
- Les fichiers frontend doivent rester sous 500 lignes. `PageLayout` doit rester
  simple et les migrations doivent éviter de surcharger `AppViewSwitch`.

## Stratégie De Migration Proposée

1. Modifier `MainMenu` en premier pour corriger les actions et préparer un
   callback `onOpenAuth` ou équivalent pour `Connexion`.
2. Adapter les styles du menu dans les classes `.pageHeaderActions` et
   `.pageHeaderOptionsTrigger`, en limitant l'impact aux actions de menu.
3. Créer `PageLayout` avec :
   - props de session/navigation ;
   - props de header (`eyebrow`, `title`, `subtitle`) ;
   - `headerClassName`, `shellClassName` et contenu de header optionnel ;
   - rendu du contenu principal ;
   - rendu de `AppFooter`.
4. Retirer `AppFrame` de `App.jsx`, puis supprimer
   `frontend/src/components/AppFrame.jsx`.
5. Migrer d'abord les pages qui utilisent déjà `MainMenu`, car leurs props sont
   presque complètes.
6. Ajouter ensuite les props communes dans `AppViewSwitch` pour les pages sans
   menu.
7. Migrer les pages sans menu en conservant leurs actions contextuelles :
   - les boutons retour peuvent devenir du contenu/action de page si nécessaire ;
   - les formulaires, tableaux et workflows restent dans les pages.
8. Valider avec `npm run build` depuis `frontend/`, puis vérifier desktop et
   mobile.
9. Rebuilder le service Docker frontend concerné après validation.
10. Terminer par la documentation :
    `documentation/menu.md`, `documentation/frontend-arch.md`, `AGENTS.md`, puis
    vérifier `documentation/site-plan.md`, `documentation/authentication.md` et
    `README.md`.

## Documentation Concernée Pour Les Tâches Suivantes

- 🟢 `documentation/menu.md` : concernée, lue, règles à préserver ou à aligner
  avec la demande `fix_menu`.
- 🟢 `documentation/frontend-arch.md` : concernée, lue, `PageLayout` doit rester
  un composant de rendu et les pages doivent rester sans logique métier.
- 🟢 `documentation/site-plan.md` : concernée, lue, les routes publiques,
  privées et admin doivent conserver leurs règles.
- 🟢 `documentation/authentication.md` : concernée, lue, la présence du menu sur
  `/auth` ne doit pas modifier le contrat d'authentification.
- 🟠 `README.md` : non concerné par l'analyse seule ; à revérifier après les
  modifications fonctionnelles.
