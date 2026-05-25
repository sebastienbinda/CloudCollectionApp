# About Page Summary

## Key Points

- The About page is the application's public unauthenticated page.
- It is rendered by `frontend/src/components/AboutView.jsx`.
- Its route is `/about`; the authenticated Ma collection page is `/collection`.
- It must not call a protected backend endpoint without a token.
- It uses the static image `/about-home-image.jpg`, extracted from the
  `Accueil` sheet of the `collection.ods` file.

## Objective

The About page presents CloudCollectionApp's features without going into
technical details. It must explain the value of the application to an
unauthenticated visitor while keeping access to sign-in and the main menu
available.

## Functional Constraints

- The page must remain accessible without authentication.
- It must not expose collection data from a backend call.
- The content must remain descriptive and non-technical.
- The text must describe use cases: exploring the collection, tracking the wish
  list, viewing the authenticated home page, and maintaining data.
- Navigation must go through `MainMenu`.
- Actions reserved for an authenticated session must remain disabled through the
  menu when the user is not signed in.

## Image

- The displayed image is `frontend/public/about-home-image.jpg`.
- This image comes from the `Accueil` sheet of `collection.ods`.
- Do not replace this image with an external URL.
- If the image in the `Accueil` sheet changes in the ODS file, re-extract the
  public asset and verify the responsive rendering.
- The image must keep clear alternative text.

## UI and Responsiveness

- The component must remain separate from `HomeView`.
- Specific styles use the classes `aboutShell`, `aboutHeader`,
  `aboutContent`, `aboutHomeImage`, `aboutIntro` and `aboutFeatureGrid`.
- The feature grid must remain readable on desktop and collapse cleanly on
  mobile.
- Avoid technical details, long lists, and overly dense text.
- Do not turn this page into a complex marketing landing page.

## Development Rules

- Also read `documentation/menu.md` before changing the page menu.
- Also read `documentation/authentication.md` before any route or page access
  change.
- After a visual or JSX change, run at least `npm run build`.
- If the public asset changes, rebuild the frontend Docker image when Docker is
  available.
