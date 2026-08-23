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
- Entries awaiting route discovery remain disabled. Entries forbidden by a
  GUEST share category or by GUEST's Configuration exclusion are omitted so
  the menu reflects the signed sharing scope exactly.

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
- The menu entry matching the current page must be highlighted on desktop and
  mobile using a muted darker green accent. When a page has no dedicated menu
  entry, the closest existing entry is highlighted instead of adding a new menu
  item.
- A click or pointer event outside the mobile secondary action panel closes it.
- The `Escape` key closes the mobile secondary action panel when it is open.
- Clicking an action closes the menu before triggering navigation.
- On desktop, navigation entries are grouped before session actions.
- On desktop, the session action remains on the right side of the navigation
  bar: `Connexion` for anonymous visitors, `Deconnexion` for authenticated
  users.
- For authenticated users on desktop, the main navigation order is
  `Ma collection`, `Liste de souhaits`, `Statistiques`, `Bibliotheque`,
  `Configuration`, `Faire un retour`, then `A propos`; `Deconnexion` remains
  the last action on the right side of the navigation bar.
- For authenticated users on mobile, `Collection`, `Souhaits`, `Stats`, `Biblio` and
  `Plus` are the primary dock entries, in that order.
- Anonymous visitors see only public/session entries: `Bibliotheque`,
  `Connexion`, `Faire un retour` and `A propos` directly in the mobile dock; the
  `Plus` entry is not rendered when no secondary action is available.
- On mobile, authenticated users see `Configuration`, `Faire un retour`,
  `A propos` and `Deconnexion` as secondary actions opened from `Plus`, with
  `Deconnexion` last.
- The secondary mobile panel closes when the mouse pointer leaves it.
- On mobile and touch devices, pointer leave must not cause accidental closing;
  filter events by `pointerType`.
- The mobile `Plus` trigger must keep `aria-expanded` and `aria-haspopup`.
- The mobile `Plus` trigger is highlighted when the active page belongs to a
  secondary mobile action hidden behind it.
- Menu icons are inline styled SVG icons. Do not replace them with letter-only
  shortcuts.
- A GUEST sees only the permitted Collection/Wishlist primary entries, followed
  by Bibliotheque and `Plus`; the dock grid adapts to the resulting item count.
  `Plus` contains Faire un retour, About and Logout, never Configuration.

## Access Constraints

- `A propos` always remains accessible and opens `/about`.
- `Faire un retour` always remains accessible and opens `/feedback`; the page
  itself decides whether the connected session can submit a protected feedback
  request.
- `Bibliotheque` always remains accessible.
  When an `ADMIN` session has Library games waiting for validation, the menu may
  show a prop-driven badge on this entry. The menu must not fetch the summary
  itself.
- `Liste de souhaits` requires an active local non-`ADMIN` collection session
  and opens `/wishlist`.
- `Ma collection` requires an active local non-`ADMIN` collection session and
  opens `/collection`.
- `Statistiques` requires an active local non-`ADMIN` collection session and
  opens `/collection/statistics`. The backend route remains the authority for
  access to `GET /collections/statistics`.
- For GUEST, Collection and Wishlist are independent: each entry is rendered
  only when its corresponding signed permission is true. Statistics follows the
  Collection permission. Configuration and all Configuration subpages are never
  rendered.
- Authenticated entries whose access is still being discovered must use
  `disabled`; entries reserved for authenticated users must not be rendered for
  anonymous visitors.
- Session actions such as `Connexion`, `Configuration` and `Deconnexion` are
  managed inside `MainMenu`; do not reintroduce a separate session dropdown.
- Once a registered user is connected, the desktop/mobile navigation identity
  displays the signed pseudonym. A GUEST displays exactly
  `Invité de <pseudonyme>` with the yellow GUEST treatment on desktop and
  mobile.
- The Library entry opens `/bibliotheque` and must remain available for
  unauthenticated visitors.
- The wishlist entry opens `/wishlist`, must be hidden from unauthenticated
  visitors, and must remain disabled for authenticated `ADMIN` users.
- For authenticated users, `Deconnexion` must stay visually and structurally
  last in both desktop and mobile navigation.
- The main menu must not expose a `Voir les jeux` entry; platform game pages
  remain reachable from collection cards and contextual navigation.

## Responsiveness

- Mobile dock entries may use short labels, but their icons must remain visible.
- The touch target must keep a comfortable minimum size.
- Do not rely only on hover: the menu must work with click/tap.
- The mobile dock must keep a compact vertical footprint and must not overlap
  the common footer content.
- The GUEST identity badge is positioned above the fixed mobile dock and must
  remain readable without hiding a dock action.
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
- When adding a new menu entry, update the full propagation chain, not only
  `MainMenu.jsx`: the application view model must expose the boolean access flag
  and navigation callback, `AppViewSwitch.buildPageLayoutProps` must pass both,
  and every routed page that renders `PageLayout` must forward both props to the
  layout. A missing callback such as `onOpenStatistics` makes `MainMenu` omit the
  entry even when the access boolean is true.
- Add or update a frontend regression test covering this propagation. At minimum,
  test that routed pages using `PageLayout` forward the new access flag and
  callback for the menu entry.
- After any menu change, run at least `npm run build`.
- For a significant visual change, verify desktop and mobile states.
