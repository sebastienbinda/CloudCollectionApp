# Main Menu Summary

## Key Points

- The main menu is handled by `frontend/src/components/MainMenu.jsx`.
- It must remain usable with a mouse, keyboard, and touchscreen.
- The menu closes on outside click, on the `Escape` key, after an action, and
  when the mouse cursor leaves the menu.
- Closing when leaving the menu must not break touch usage.
- Unavailable entries must be disabled rather than hidden.

## Objective

The main menu gives access to cross-application views from the A propos and Ma
collection pages. It must not contain business logic: it triggers callbacks
provided by `App.jsx` and only reflects the session state received through
props.

## Expected Behavior

- The main button opens and closes the menu.
- A click or pointer event outside the menu closes the menu.
- The `Escape` key closes the menu when it is open.
- Clicking an action closes the menu before triggering navigation.
- On desktop, the menu closes when the mouse pointer leaves it.
- A transition area between the button and the panel may remain active to avoid
  accidental closing while moving the mouse.
- On mobile and touch devices, pointer leave must not cause accidental closing;
  filter events by `pointerType`.
- The menu must keep `aria-expanded` and `aria-haspopup` on the trigger button.

## Access Constraints

- `A propos` always remains accessible and opens `/about`.
- `Bibliotheque` always remains accessible.
- `Ma collection` requires an active local session and opens `/collection`.
- Inaccessible entries must use `disabled`.
- The session menu remains managed by `AuthStatusMenu`.
- The Library entry opens `/bibliotheque` and must remain available for
  unauthenticated visitors.
- The main menu must not expose a `Voir les jeux` entry; platform game pages
  remain reachable from collection cards and contextual navigation.

## Responsiveness

- The `Menu` label may be hidden on mobile, but the icon must remain visible.
- The touch target must keep a comfortable minimum size.
- Do not rely only on hover: the menu must work with click/tap.
- The panel must remain positioned below the button and must not overlap the
  authentication button.

## Development Rules

- Do not reintroduce an uncontrolled `<details>` element if closing behavior must
  remain precise.
- Do not add an external dependency for this menu.
- Keep menu logic in `MainMenu.jsx`; pages must not manage its open/closed state.
- Routes and navigation remain centralized in `App.jsx` and
  `AppRouting`.
- After any menu change, run at least `npm run build`.
- For a significant visual change, verify desktop and mobile states.
