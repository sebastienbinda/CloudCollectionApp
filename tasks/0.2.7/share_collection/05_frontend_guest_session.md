# Activation de la session invitée

## Objectif

Traiter `/collection/share/<token>`, créer la session GUEST et retirer le token
de l'URL avant d'afficher la collection.

## Dépendances

- Sous-tâches 02 à 04 terminées.

## Périmètre

- Lire `documentation/frontend-arch.md`, `documentation/authentication.md` et
  `documentation/site-plan.md`.
- Ajouter la détection de la route `/collection/share/<token>`.
- Appeler le service frontend d'échange du token de lien contre une session
  Bearer.
- Stocker la session avec les mécanismes existants, puis utiliser
  `history.replaceState` pour retirer immédiatement le token de l'URL.
- Rediriger vers `/collection` si la collection est autorisée, sinon vers
  `/wishlist` si seule la wishlist est autorisée.
- Si une session locale existe déjà, la remplacer uniquement après un échange
  réussi afin de ne pas perdre une session valide sur un lien incorrect.
- Traiter HTTP `411` sur tout appel authentifié GUEST : effacer la session,
  rediriger vers `/about` et afficher un message de partage expiré ou révoqué.
- Ne pas assimiler un `403` de permission GUEST à une révocation.
- Conserver le comportement existant d'expiration des sessions USER et ADMIN.

## Hors périmètre

- Écran propriétaire de création des liens.
- Adaptation visuelle des pages collection et wishlist.

## Tests attendus

- Échange réussi et suppression du token dans l'URL.
- Redirection selon les permissions collection et wishlist.
- Lien invalide sans destruction préalable d'une session existante.
- Déconnexion et retour à About après `411`.
- Un `403` de permission GUEST ne déclenche pas la logique de révocation.

## Critères d'acceptation

- Le token du lien ne reste ni dans l'adresse affichée ni dans l'historique de
  navigation après l'échange.
- La session GUEST utilise les services et hooks de session existants.
- Le build frontend passe.
