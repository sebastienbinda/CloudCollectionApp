# Main Menu Summary

## Key Points

- The unified application menu is rendered by
  `frontend/src/components/PageLayout.jsx` through
  `frontend/src/components/MainMenu.jsx`.
- It must remain usable with a mouse, keyboard, and touchscreen.
- The menu closes on outside click, on the `Escape` key, after an action, and
  when the mouse cursor leaves the menu.
- Closing when leaving the menu must not break touch usage.
- Unavailable entries must be disabled rather than hidden.

## Objective

The main menu gives access to cross-application views and session actions from
all routed pages using `PageLayout`. It must not contain business logic: it
triggers callbacks provided by the application view model and only reflects the
session state received through props.

## Expected Behavior

- The main button opens and closes the menu.
- Menu entries must be rendered as `<button>` elements.
- A click or pointer event outside the menu closes the menu.
- The `Escape` key closes the menu when it is open.
- Clicking an action closes the menu before triggering navigation.
- Menu entries from navigation and session actions must be presented in
  alphabetical order.
- The session action is always the last menu entry: `Connexion` for anonymous
  visitors, `Deconnexion` for authenticated users.
- On desktop, the menu closes when the mouse pointer leaves it.
- A transition area between the button and the panel may remain active to avoid
  accidental closing while moving the mouse.
- On mobile and touch devices, pointer leave must not cause accidental closing;
  filter events by `pointerType`.
- The menu must keep `aria-expanded` and `aria-haspopup` on the trigger button.

## Access Constraints

- `A propos` always remains accessible and opens `/about`.
- `Bibliotheque` always remains accessible.
- `Liste de souhaits` requires an active local non-`ADMIN` collection session
  and opens `/wishlist`.
- `Ma collection` requires an active local session and opens `/collection`.
- Inaccessible entries must use `disabled`.
- Session actions such as `Connexion`, `Configuration` and `Deconnexion` are
  managed inside `MainMenu`; do not reintroduce a separate session dropdown.
- Once a user is connected, the header displays
  `Utilisateur connecte : <email>` on the top right outside the menu.
- The Library entry opens `/bibliotheque` and must remain available for
  unauthenticated visitors.
- The wishlist entry opens `/wishlist` and must remain disabled for
  unauthenticated visitors and `ADMIN` users.
- The main menu must not expose a `Voir les jeux` entry; platform game pages
  remain reachable from collection cards and contextual navigation.

## Responsiveness

- The `Menu` label may be hidden on mobile, but the icon must remain visible.
- The touch target must keep a comfortable minimum size.
- Do not rely only on hover: the menu must work with click/tap.
- The panel must remain positioned below the button and must not overlap the
  connected-user indicator displayed on the top right.

## Development Rules

- Do not reintroduce an uncontrolled `<details>` element if closing behavior must
  remain precise.
- Do not add an external dependency for this menu.
- Keep menu logic in `MainMenu.jsx`; pages must not manage its open/closed state.
- Pages must use `PageLayout` for the shared header and must not import
  `MainMenu` directly.
- Routes and navigation remain centralized in `App.jsx` and
  `AppRouting`.
- After any menu change, run at least `npm run build`.
- For a significant visual change, verify desktop and mobile states.
