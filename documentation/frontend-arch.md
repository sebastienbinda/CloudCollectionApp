# Frontend Architecture Rules

## Purpose

This document defines the frontend code architecture to preserve when changing
React, Vite, frontend hooks, frontend services, pages or shared UI components.

## Core Principles

- `frontend/src/App.jsx` must remain the React composition entry point only.
- `App.jsx` must not contain data loading, routing decisions, API calls,
  filtering, sorting or form business workflows.
- React components under `frontend/src/components/` must focus on rendering,
  layout, user interaction and local UI-only state.
- Every routed React page must use `frontend/src/components/PageLayout.jsx` for
  the shared shell, header, main menu and footer.
- Routed pages must not recreate their own application header, main menu or
  footer. Page-specific header content must be injected through `PageLayout`
  props such as `headerLeadingContent`, `titleContent`, `headerExtraContent` or
  `headerAsideContent`.
- Frontend API calls must remain in `frontend/src/services/`.
- Reusable calculations must remain in pure utility modules such as
  `frontend/src/collectionUtils.js`.
- Application state orchestration must live in domain hooks under
  `frontend/src/hooks/`.
- Each page must be reactive to be well displayed on modern mobile resolutions.
- Keep frontend files under 500 lines. Split by domain before a file reaches
  that limit.

## Hook Domains

Use the following domain folders for new or modified hooks:

- `frontend/src/hooks/app/`: application composition, session state and
  view-model assembly.
- `frontend/src/hooks/navigation/`: current view, URL synchronization,
  history handling and route redirection.
- `frontend/src/hooks/collection/`: cross-page collection refresh signals, plus
  connected-user collection onboarding, detailed statistics and import state.
- `frontend/src/hooks/home/`: connected-user collection statistics and home
  search.
- `frontend/src/hooks/platforms/`: platform catalog loading and platform
  selection initialization.
- `frontend/src/hooks/games/`: platform game collection, game filtering,
  sorting, editing, game detail and add-game form workflows.
- `frontend/src/hooks/library/`: public Library counters, public entity search,
  server-side pagination, backend-driven sorting for platforms, studios and
  games, and Library administration actions exposed from Configuration.

## Current Entry Points

- `frontend/src/App.jsx` delegates active view rendering to `AppViewSwitch` and
  mounts `AuthSessionModal`.
- `frontend/src/hooks/app/useCloudCollectionViewModel.js` composes domain hooks
  into `viewProps` and `authModalProps`.
- `frontend/src/components/AppViewSwitch.jsx` maps `currentView` to page
  components.
- `frontend/src/components/PageLayout.jsx` owns the shared page shell, renders
  the page header, mounts `MainMenu` as a shared navigation element outside the
  header, renders the common scroll-to-top control, and renders the common
  footer.

## Responsibilities

### `hooks/app`

- Compose domain hooks.
- Prepare props consumed by `AppViewSwitch`.
- Centralize frontend session state with `useSessionState`.
- Activate transient `/collection/share/<token>` links in
  `useCollectionShareSession`: clear an existing local session, remove the raw
  token from browser history, exchange it through the dedicated service, then
  select the first permitted GUEST destination.
- Derive GUEST display permissions and owner labels from signed claims through
  `GuestSessionViewPolicy`; components must not decode or reinterpret claims.
- Avoid direct API calls except through composed domain hooks.

### `hooks/navigation`

- Own `currentView` and `selectedPlatform`.
- Own browser history updates and `popstate` behavior.
- Preserve unauthenticated redirection rules from `documentation/site-plan.md`.
- Preserve the frontend-only `ADMIN` collection exclusion from
  `documentation/site-plan.md`: `ADMIN` keeps backend rights but must not open
  collection ownership views.
- Do not fetch backend data.
- Apply `GuestNavigationPolicy` for direct navigation and callbacks. A GUEST
  cannot open Configuration or mutation/import views and is redirected to
  Collection, then Wishlist, then About according to permissions.

### `hooks/collection`

- Own cross-page collection refresh behavior.
- Own the connected-user collection onboarding workflow.
- Call `GET /api/users/me/collection` after sign-in to decide whether the user
  can continue to `/collection` or must visit `/collection/import`.
- Skip the collection-status check for the configured `ADMIN` account and route
  it to `/configuration` instead, because `ADMIN` is not a frontend collection
  owner.
- Call `POST /api/users/import/file/<file_type>` with `FormData`, then
  `POST /api/users/import/analyze/<file_type>` to prefill sheet choices, then
  `POST /api/users/import` with JSON configuration. The backend owns validation
  and persistence decisions.
- After file analysis, call `GET /api/users/import/` to retrieve the last saved
  import configuration. Apply it to the form only after explicit user
  confirmation.
- Display the import summary after a successful import and expose a user action
  to open `/collection`. Redirect to `/collection` only when the status route
  confirms `has_collection: true` outside the just-finished import workflow.
- Reuse the same onboarding hook and route for additive imports opened from
  Configuration. The Configuration page only triggers navigation; it must not
  own file upload, analysis, validation or persistence state.
- Own the connected-user collection reinitialization workflow in a dedicated
  hook separate from onboarding. The hook calls
  `POST /api/users/collection/reinit`, refreshes collection signals and opens
  `/collection/import` after success.
- Own collection-share management state in `useCollectionShareManagement`.
  Keep form validation in `collectionShareForm.js`, HTTP details in
  `CollectionSharesApi`, and clipboard/confirmation actions in the hook. The
  routed owner page only renders this state.
- Own detailed collection statistics loading in `useCollectionStatisticsPage`.
  It must call `GET /collections/statistics` through `CollectionStatisticsApi`
  and must not recalculate backend chart distributions from game lists.

### `hooks/home`

- Own connected-user collection statistics loading.
- Own home search state and search submissions.
- Load collection statistics and searches as owned collection data, not
  wishlist data.

### `hooks/platforms`

- Own platform list loading.
- Load connected-user collection platforms from backend SQL endpoints.
- Request `wishlist=false` for collection platform lists so wishlist-only
  platforms do not appear in Ma collection.
- Initialize selected platform from URL or first available platform.

### `hooks/games`

- Own platform game loading.
- Request `wishlist=false` for collection game lists.
- Own wishlist game loading for `/wishlist` and request `wishlist=true`.
- Own the wishlist buy-status filter, persist it in the
  `wishlist_buy_status` URL query parameter and initialize it from the GUEST
  `wishlist_buy_status_default_filter` claim when no query parameter exists.
- Own table filters, sorting and derived game collections.
- Own game detail loading for `/collection/jeux/<game_id>` through protected
  collection endpoints.
- Game detail ownership indicators must be derived in the game detail hook:
  collection detail is owned by definition, while Library detail may check the
  protected collection detail endpoint and silently treat a missing row as not
  owned.
- Request supported collection and wishlist sort orders from the backend with
  the `sort` query parameter. Do not recalculate backend list ordering in React
  for collection consultation pages.
- Own add-game form state and future submit workflow while backend actions
  remain reserved.
- Use services for backend calls and utilities for pure transforms.

### `hooks/library`

- Own public Library counters, Library home game search and entity list
  loading.
- Own Library search input state, applied search criteria, pagination state and
  backend sort state.
- Keep `/api/library/*` calls in `frontend/src/services/LibraryApi.js`.
- Keep public Library home game search in a dedicated library hook; it must
  query global reference games through `LibraryApi`, not connected-user
  collection endpoints.
- Public game detail opened from Library pages must query
  `/api/library/games/<game_id>` through `LibraryApi`.
- Public platform detail opened from Library pages must query
  `/api/library/platforms/<platform_id>` through `LibraryApi`.
- Public platform detail displays accepted platform images returned by the
  platform detail payload. Image URLs are built by `LibraryApi` from the public
  accepted-image endpoint with cache-busting when needed.
- Authenticated non-`ADMIN` users may upload a proposed platform image from
  public platform detail through `LibraryApi.uploadPlatformImage`. The component
  owns only file selection and display; the hook owns upload state and messages.
- Provide pagination metadata and callbacks to `TableComponent`; pages must not
  render their own table pagination controls.
- Do not add authentication headers to public Library endpoints, except
  `/api/library/games` may send a locally non-expired Bearer to request the
  optional `in_current_user_collection` and `in_current_user_wishlist` markers.
  Expired local tokens must not be sent for this optional enrichment.
- Public Library and collection game detail may show the protected
  duplicate-report action to a connected `USER` only after the
  collection-status hook confirms that the user has an imported collection. The
  hook must ask for explicit confirmation before calling
  `LibraryApi.reportGameDuplicate`; the component only renders the provided
  action state.
- Keep protected Library administration calls in a dedicated admin service and
  user-triggered hooks. They must use route discovery before being displayed and
  must not change the public read-only Library consultation routes.
- The Bibliotheque games list may expose the `duplicate_flag` filter only to
  `ADMIN` sessions. The hook owns this criterion and sends it to the backend;
  the generic list component only renders the provided filter state.
- The same list may expose the `status` filter and validation/refusal selection
  workflow only when route discovery grants game validation administration. The
  state stays in `useLibraryGames`, protected calls stay in `LibraryAdminApi`,
  and the generic list component renders only the provided controls, messages
  and callbacks.
- Game duplicate correction belongs to the Library admin frontend domain:
  protected HTTP calls stay in `LibraryAdminApi`, state and user actions stay in
  `useGameDuplicateAdminPage`, and `/configuration/doublons/<game_id>` must be
  rendered through `AppViewSwitch` and `PageLayout`. Reject and merge outcomes
  must be rendered as a dedicated result state, not as raw JSON below the
  correction form.
- Platform image moderation belongs to the Library admin frontend domain:
  protected HTTP calls stay in `LibraryAdminApi`, state and user actions stay in
  `usePlatformImageModeration`, and the Configuration section only renders the
  filters, paginated `TableComponent`, thumbnails, preview dialog and action
  buttons.

### User Administration

- Keep user administration API calls in `frontend/src/services/UsersApi.js`.
- Keep the `/users` page focused on display, filters and user-triggered
  actions.
- Validate waiting users only through the backend `POST
  /api/users/<id>/validate` route when route discovery confirms access.
- Keep activation email sign-in links on `/auth?email=<address>` frontend-only:
  if the requested account is already connected, open `/about`; if another
  account is connected, display a sign-out choice before reconnecting with the
  requested account.
- Support the `status=WAITING_VALIDATION` query parameter on `/users` as a
  backend search filter for administrator notification links.

### `services`

- Keep HTTP details, URLs, headers and response normalization in services.
- Use the shared backend availability guard for calls to backend routes so a
  stopped backend or proxy `502`/`503`/`504` responses cannot trigger unbounded
  automatic request loops.
- Do not put React state in services.
- Do not duplicate token logic outside existing auth/API services.
- Keep public link exchange isolated in `CollectionShareSessionApi`: it must not
  attach an existing Authorization header. Keep owner management HTTP calls in
  `CollectionSharesApi` with normal Bearer headers.
- Keep GUEST presentation and navigation decisions in the pure
  `GuestSessionViewPolicy` and `GuestNavigationPolicy` classes so permission
  combinations remain unit-testable without React.

### Page Components

- New routed page components must be rendered by `AppViewSwitch` with the common
  page-layout props produced by `buildPageLayoutProps`.
- New routed page components must receive the shared navigation callbacks from
  `PageLayout` props and forward them to `PageLayout`.
- New routed page components must not import `MainMenu` directly. `MainMenu`
  remains an implementation detail of `PageLayout`.
- Dialogs, popovers and embedded widgets may use local headers when they are not
  full routed pages.
- `CollectionShareManagementView` is routed at `/configuration/partages`, uses
  `PageLayout`, and contains display and user interactions only. Creation,
  listing, revocation, recipient capture, validation and permission decisions
  remain outside the component.

## GUEST Presentation

- `MainMenu` receives separate `canViewCollection`, `canViewWishlist` and
  `canAccessConfiguration` props. It omits non-shared category entries for
  GUEST while preserving Library, About and Logout.
- `PageLayout` carries the same access props to the shared desktop/mobile menu.
- GUEST identity is `Invité de <pseudonyme>` with a yellow treatment in both
  responsive variants. Shared collection and wishlist pages display their
  owner-aware subtitle on desktop and mobile.
- Components may hide mutation actions and missing price fields, but backend
  authorization and response filtering remain authoritative.
- Price normalization must preserve absence: `VideoGamesApi` must not create
  `purchase_price` or `priceUnit` when the backend omitted the source fields.

## Architecture Decisions

### Backend Availability Guard

Frontend backend calls must go through a shared availability guard in
`frontend/src/services/`. The guard is a frontend resilience mechanism, not a
security boundary.

The guard must:

- wrap every direct `fetch` call to application backend routes;
- count consecutive transport failures and proxy/backend unavailable responses
  such as `502`, `503` and `504`;
- temporarily stop automatic backend calls after the configured failure
  threshold is reached;
- reset its failure state after a successful backend response;
- stay independent from React state so it can be reused by every API service.

Hooks and components must not implement their own retry loops, polling loops or
backend-down throttling. They should call domain services and display the
normalized error state they receive. User-triggered actions may still attempt a
backend call after the guard cooldown has elapsed.

The guard must not:

- clear or validate Bearer tokens;
- decide user permissions;
- hide authorization errors such as `401` or `403`;
- replace backend route protection or backend rate limiting.

## Validation

After frontend architecture changes:

- run `npm run build` from `frontend/`;
- rebuild the Docker `web` service when runtime frontend code changes;
- verify whether `README.md`, `documentation/site-plan.md`,
  `documentation/authentication.md` or this document must be updated;
- when frontend pages or navigation behavior change, explicitly report whether
  every rule from `documentation/site-plan.md` remains respected.
