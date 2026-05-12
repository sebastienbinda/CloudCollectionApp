# AGENTS.md

## General Principles

- Prefer maintainable, modular, and reusable code.
- Respect existing project architecture and conventions.
- Use explicit naming for classes, methods, variables, and files.
- Before creating new code, always search for existing similar implementations in the project.
- Reuse existing patterns and utilities whenever possible.
- Avoid introducing new frameworks or dependencies unless necessary. If it is necessary ask for confirmation before adding any new framework or dependency.
- Always use English for files and class names.

## Architecture

- Prefer object-oriented design and SOLID principles.
- Organize code by feature/domain.
- Keep business logic in the backend whenever possible.
- Frontend should mainly handle display and user interactions.
- For database models, use one class and one file for each model in the backend ORM.

## Size Constraints

- Never create source files longer than 500 lines unless strictly necessary.
- Never create methods longer than 150 lines unless strictly necessary.

## Code Documentation

- Add documentation comments for all public classes and methods in French.
- Include parameter, return type, and exception descriptions.
- Add a file header to all new source files containing:
  - project name
  - creation date
  - authors: OpenAI ChatGPT, Codex, Binda Sébastien
  - Apache 2.0 license

## Security

- Never hardcode secrets, passwords, or tokens.

## Tests and Validation

- Always create or update backend unit tests when modifying logic.
- Run and validate tests after each code modification.
- Rebuild Docker images when changes impact runtime behavior.

## Frontend Assets

- When changing a public frontend asset without changing its filename or path, update every application reference with a new cache-busting version parameter.

## Functional Documentation to Respect

- Before changing authentication, backend route protection, frontend session handling, or access control, read and respect `documentation/authentication.md`.
- Before changing the main navigation menu, responsive menu behavior, or shared menu actions, read and respect `documentation/menu.md`.
- Before changing the public About page, its route, copy, image, or responsive layout, read and respect `documentation/about.md`.
- Before adding or modifying any frontend page, read and respect `documentation/site-plan.md`.

## Change Governance

- Ask for explicit confirmation before making any modification that changes a paradigm, invariant, or expected behavior described in any related `documentation/*.md` file.
- When adding or modifying any frontend page, explicitly state whether the rules from `documentation/site-plan.md` were respected for every site page.
- When adding a new feature, propose updates to existing `documentation/*.md` files if the feature changes an already documented area, and wait for confirmation before applying those documentation changes.
- When adding a new feature that creates a completely new functional block, propose creating a new `documentation/*.md` file for that block, and wait for confirmation before creating it.
- After each code modification, verify whether `README.md` must be updated to reflect changed behavior, commands, configuration, routes, dependencies, CI, Docker usage, or user-facing features; update it in the same change set when needed.
- After each code modification, state whether the rules from each `documentation/*.md` file related to the request were respected, with one explicit information line per documentation file.
- In the documentation compliance report, prefix each documentation filename with a visible colored status marker instead of the color name: 🟢 only when the file is concerned, verified, and respected; 🟠 when the file is not concerned; and 🔴 when the file is concerned but conflicting, not respected, or verified and found not respected.
