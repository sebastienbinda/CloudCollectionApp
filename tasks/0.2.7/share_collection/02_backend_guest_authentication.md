# Profil GUEST et échange du lien de partage

## Objectif

Introduire le profil `GUEST` et transformer un token présent dans un lien en
session Bearer invitée limitée au partage concerné.

## Dépendance

- Sous-tâche 01 terminée.

## Périmètre

- Lire `documentation/authentication.md`, `documentation/backend-arch.md` et
  `documentation/users.md`.
- Ajouter `GUEST` à la gestion des profils sans lui faire hériter des droits
  `USER` ou `ADMIN`.
- Signer un token de lien temporaire contenant l'identifiant du partage, puis
  vérifier sa signature et sa date d'expiration.
- Ajouter un endpoint public d'échange recevant le token du lien et retournant
  un Bearer de session `GUEST`.
- Charger le propriétaire et les permissions depuis la base pendant l'échange,
  sans faire confiance aux seules valeurs du lien.
- Inclure dans la session GUEST : profil, identifiant du partage, identifiant
  du propriétaire, pseudonyme courant du propriétaire, permissions, dates
  d'émission et d'expiration.
- Limiter l'expiration de la session à celle du partage.
- Vérifier l'état du partage et du propriétaire lors de chaque appel protégé
  effectué avec la session GUEST.
- Retourner HTTP `411` lorsque le partage est expiré, révoqué ou lorsque son
  propriétaire est supprimé ou verrouillé.
- Exposer correctement le profil `GUEST` dans la découverte de routes.

## Hors périmètre

- Routes de création, liste et révocation par le propriétaire.
- Lecture effective des jeux.
- Frontend.

## Tests attendus

- Échange réussi d'un lien valide.
- Refus d'un lien falsifié ou inconnu.
- Réponse `411` pour un partage expiré ou révoqué.
- Réponse `411` pour un propriétaire verrouillé ou supprimé.
- `GUEST` ne satisfait aucune route exigeant `USER` ou `ADMIN` par héritage.
- Claims et durée de la session conformes.

## Critères d'acceptation

- Le token disparaissant ensuite de l'URL peut être remplacé par une session
  Bearer autonome mais révocable.
- La révocation est constatée au prochain appel backend, sans polling.
- Les tests backend ciblés passent.
