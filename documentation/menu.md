# Main Menu Summary

## Key Points

- The unified application menu is rendered by
  `frontend/src/components/PageLayout.jsx` through
  `frontend/src/components/MainMenu.jsx`.
- The menu is structurally separated from the page header: `PageLayout` renders
  the header first, then the shared navigation bar, then the page content.
- It must remain usable with a mouse, keyboard, and touchscreen.
- Secondary mobile actions close on outside click, on the `Escape` key, after
  an action, and when the mouse cursor leaves the menu.
- Closing when leaving the menu must not break touch usage.
- Unavailable entries must be disabled rather than hidden.

## Objective

The main menu gives access to cross-application views and session actions from
all routed pages using `PageLayout`. It must not contain business logic: it
triggers callbacks provided by the application view model and only reflects the
session state received through props.

## Expected Behavior

- On desktop, the primary navigation entries are visible directly in a compact
  horizontal navigation bar.
- On mobile, the primary navigation is displayed as a fixed bottom dock with
  compact icon actions.
- The mobile `Plus` button opens and closes the secondary action panel.
- Menu entries must be rendered as `<button>` elements.
- A click or pointer event outside the mobile secondary action panel closes it.
- The `Escape` key closes the mobile secondary action panel when it is open.
- Clicking an action closes the menu before triggering navigation.
- On desktop, navigation entries are grouped before session actions.
- On desktop, the session action remains on the right side of the navigation
  bar: `Connexion` for anonymous visitors, `Deconnexion` for authenticated
  users.
- On mobile, `Bibliotheque`, the collection/session shortcut, `Liste de
  souhaits` and `Plus` are the primary dock entries.
- On mobile, anonymous visitors see `Connexion` in the primary dock slot that
  authenticated collection users use for `Ma collection`.
- On mobile, `A propos`, `Configuration` and authenticated `Deconnexion` are
  secondary actions opened from `Plus`.
- The secondary mobile panel closes when the mouse pointer leaves it.
- On mobile and touch devices, pointer leave must not cause accidental closing;
  filter events by `pointerType`.
- The mobile `Plus` trigger must keep `aria-expanded` and `aria-haspopup`.
- Menu icons are inline styled SVG icons. Do not replace them with letter-only
  shortcuts.

## Access Constraints

- `A propos` always remains accessible and opens `/about`.
- `Bibliotheque` always remains accessible.
- `Liste de souhaits` requires an active local non-`ADMIN` collection session
  and opens `/wishlist`.
- `Ma collection` requires an active local non-`ADMIN` collection session and
  opens `/collection`.
- Inaccessible entries must use `disabled`.
- Session actions such as `Connexion`, `Configuration` and `Deconnexion` are
  managed inside `MainMenu`; do not reintroduce a separate session dropdown.
- Once a user is connected, the desktop navigation area displays
  `Utilisateur connecte : <email>` next to the session action.
- The Library entry opens `/bibliotheque` and must remain available for
  unauthenticated visitors.
- The wishlist entry opens `/wishlist` and must remain disabled for
  unauthenticated visitors and `ADMIN` users.
- The main menu must not expose a `Voir les jeux` entry; platform game pages
  remain reachable from collection cards and contextual navigation.

## Responsiveness

- Mobile dock entries may use short labels, but their icons must remain visible.
- The touch target must keep a comfortable minimum size.
- Do not rely only on hover: the menu must work with click/tap.
- The mobile dock must keep a compact vertical footprint and must not overlap
  the common footer content.
- The mobile secondary panel opens above the dock so it remains reachable
  without adding height to the page header.
- The desktop menu must remain visually below the page header, not above it.

## Development Rules

- Do not reintroduce an uncontrolled `<details>` element if closing behavior must
  remain precise.
- Do not add an external dependency for this menu.
- Keep menu logic in `MainMenu.jsx`; pages must not manage its open/closed state.
- Pages must use `PageLayout` for the shared shell and must not import
  `MainMenu` directly.
- Routes and navigation remain centralized in the navigation hook and the
  application view model.
- After any menu change, run at least `npm run build`.
- For a significant visual change, verify desktop and mobile states.
