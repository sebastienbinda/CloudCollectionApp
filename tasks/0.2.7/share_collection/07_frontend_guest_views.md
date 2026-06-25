# Navigation et vues GUEST

## Objectif

Adapter les pages de consultation et le menu aux permissions de la session
GUEST sans exposer d'action de modification.

## Dépendances

- Sous-tâches 04 à 06 terminées.

## Périmètre

- Lire `documentation/frontend-arch.md`, `documentation/site-plan.md`,
  `documentation/menu.md` et `documentation/collection.md`.
- Afficher l'identité `Invité de <pseudonyme>` avec l'accent visuel jaune
  prévu, sur desktop et mobile.
- Afficher `Collection de <pseudonyme>` sur la collection et les pages de jeux
  d'une plateforme pour GUEST uniquement.
- Afficher `Liste de souhaits de <pseudonyme>` sur la wishlist pour GUEST
  uniquement.
- Masquer Collection ou Wishlist lorsque la permission correspondante manque.
- Masquer Configuration et toutes ses sous-pages pour GUEST, y compris par
  navigation directe.
- Laisser Bibliothèque, À propos et Déconnexion accessibles.
- Masquer ou désactiver toutes les actions de mutation : ajout, édition,
  suppression, import, réinitialisation et proposition d'image.
- Ne pas afficher les prix absents du payload et ne pas les recalculer côté
  frontend.
- Conserver les comportements USER et ADMIN existants.
- Vérifier les titres et sous-titres sur desktop et mobile.

## Hors périmètre

- Gestion backend des permissions.
- Écran propriétaire de gestion des liens.

## Tests et validations attendus

- Menus pour chaque combinaison de permissions GUEST.
- Redirection des routes Configuration et sous-routes.
- Identité jaune et sous-titres adaptés.
- Absence d'actions de mutation.
- Non-régression USER, ADMIN et visiteur anonyme.
- Build frontend réussi.

## Critères d'acceptation

- Les restrictions visuelles reflètent exactement les permissions backend sans
  être utilisées comme frontière de sécurité.
- Toutes les pages concernées restent utilisables sur mobile.
