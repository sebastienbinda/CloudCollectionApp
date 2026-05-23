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
- Frontend API calls must remain in `frontend/src/services/`.
- Reusable calculations must remain in pure utility modules such as
  `frontend/src/collectionUtils.js`.
- Application state orchestration must live in domain hooks under
  `frontend/src/hooks/`.
- Keep frontend files under 500 lines. Split by domain before a file reaches
  that limit.

## Hook Domains

Use the following domain folders for new or modified hooks:

- `frontend/src/hooks/app/`: application composition, session state and
  view-model assembly.
- `frontend/src/hooks/navigation/`: current view, URL synchronization,
  history handling and route redirection.
- `frontend/src/hooks/collection/`: cross-page collection refresh and cache
  actions.
- `frontend/src/hooks/home/`: home dashboard data, protected home images and
  home search.
- `frontend/src/hooks/platforms/`: platform catalog loading and platform
  selection initialization.
- `frontend/src/hooks/games/`: platform game collection, game filtering,
  sorting, editing and add-game form workflows.
- `frontend/src/hooks/wishlist/`: wishlist-specific mutations and transfer
  actions.

## Current Entry Points

- `frontend/src/App.jsx` renders `AppFrame`, delegates active view rendering to
  `AppViewSwitch`, and mounts `AuthSessionModal`.
- `frontend/src/hooks/app/useCloudCollectionViewModel.js` composes domain hooks
  into `viewProps` and `authModalProps`.
- `frontend/src/components/AppViewSwitch.jsx` maps `currentView` to page
  components.

## Responsibilities

### `hooks/app`

- Compose domain hooks.
- Prepare props consumed by `AppViewSwitch`.
- Centralize frontend session state with `useSessionState`.
- Avoid direct API calls except through composed domain hooks.

### `hooks/navigation`

- Own `currentView` and `selectedPlatform`.
- Own browser history updates and `popstate` behavior.
- Preserve unauthenticated redirection rules from `documentation/site-plan.md`.
- Do not fetch backend data.

### `hooks/home`

- Own home dashboard loading.
- Own home search state and search submissions.
- Own protected platform image object URLs and URL cleanup.

### `hooks/platforms`

- Own platform list loading.
- Filter technical ODS sheets that must not appear as user platforms.
- Initialize selected platform from URL or first available platform.

### `hooks/games`

- Own platform game loading.
- Own table filters, sorting and derived game collections.
- Own add-game form state, suggestions and submit workflow.
- Use services for backend calls and utilities for pure transforms.

### `hooks/wishlist`

- Own wishlist edit, delete and transfer workflows.
- Keep wishlist-specific API behavior out of generic app hooks.

### `services`

- Keep HTTP details, URLs, headers and response normalization in services.
- Do not put React state in services.
- Do not duplicate token logic outside existing auth/API services.

## Validation

After frontend architecture changes:

- run `npm run build` from `frontend/`;
- rebuild the Docker `web` service when runtime frontend code changes;
- verify whether `README.md`, `documentation/site-plan.md`,
  `documentation/authentication.md` or this document must be updated;
- when frontend pages or navigation behavior change, explicitly report whether
  every rule from `documentation/site-plan.md` remains respected.
