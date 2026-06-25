# API propriétaire de gestion des partages

## Objectif

Permettre à un utilisateur `USER` de créer, lister et révoquer ses propres
partages de collection.

## Dépendances

- Sous-tâches 01 et 02 terminées.

## Périmètre

- Lire `documentation/backend-api.md`, `documentation/authentication.md` et
  `documentation/backend-arch.md`.
- Ajouter des endpoints protégés `USER` pour créer, lister et révoquer les
  partages du propriétaire connecté.
- Valider une durée entière comprise entre 1 et 240 heures.
- Valider explicitement les trois permissions booléennes : collection,
  wishlist et informations de prix.
- Refuser la création d'un partage qui ne donne accès ni à la collection ni à
  la wishlist.
- Retourner lors de la création le lien `/collection/share/<token>` signé.
- Retourner dans la liste : identifiant, dates, permissions, statut calculé
  `ACTIVE`, `EXPIRED` ou `REVOKED`, et lien recopiable reconstruit par le
  backend.
- Garantir qu'un utilisateur ne peut ni voir ni révoquer le partage d'un autre
  propriétaire.
- Rendre la révocation idempotente.
- Ajouter les métadonnées de route discovery nécessaires au futur écran.

## Hors périmètre

- Consultation des jeux avec une session GUEST.
- Interface frontend.
- Suppression physique des partages expirés ou révoqués.

## Tests attendus

- Création valide aux bornes 1 et 240 heures.
- Refus des durées et permissions invalides.
- Refus d'un partage sans collection ni wishlist.
- Isolation de la liste et de la révocation par propriétaire.
- Statuts actif, expiré et révoqué correctement sérialisés.
- Lien signé présent dans les réponses attendues.

## Critères d'acceptation

- Seul le propriétaire gère ses partages.
- Les contrats HTTP sont cohérents et testés.
- Les tests backend ciblés passent.
