# Consultation de collection par un invité

## Objectif

Autoriser un profil `GUEST` à consulter uniquement les données du propriétaire
et les catégories accordées par le partage.

## Dépendances

- Sous-tâches 01 à 03 terminées.

## Périmètre

- Lire `documentation/collection.md`, `documentation/backend-api.md`,
  `documentation/authentication.md` et `documentation/backend-arch.md`.
- Adapter les endpoints de statistiques, plateformes, recherche de jeux et
  détail de jeu pour accepter une session GUEST valide en lecture seule.
- Résoudre l'identifiant de collection depuis le propriétaire du partage et
  jamais depuis un paramètre envoyé par le client.
- Appliquer la permission collection aux données `wishlist=false` et la
  permission wishlist aux données `wishlist=true`.
- Retourner `403` lorsqu'une session GUEST valide demande une catégorie non
  accordée, sans transformer ce refus en invalidation du partage.
- Lorsque la permission prix est absente, retirer `purchase_price` et
  `price_unit` des jeux et retourner zéro pour les sommes et moyennes de prix.
- Appliquer le masquage aux listes, détails et statistiques globales ou par
  plateforme.
- Autoriser recherche, filtres et détails de plateforme en lecture.
- Interdire explicitement au profil GUEST le téléchargement ODS, l'import, la
  réinitialisation, l'ajout ou modification de jeu et l'ajout d'image.
- Conserver inchangés les droits des profils USER et ADMIN.

## Hors périmètre

- Navigation et rendu frontend.
- Gestion des partages par le propriétaire.

## Tests attendus

- Isolation stricte sur la collection du propriétaire partagé.
- Combinaisons collection seule, wishlist seule et les deux.
- Masquage complet des prix dans listes, détails et statistiques.
- `403` pour une catégorie non accordée.
- `411` après expiration ou révocation au prochain appel.
- Toutes les routes de mutation et le téléchargement refusent GUEST.
- Non-régression USER et ADMIN.

## Critères d'acceptation

- Aucun identifiant utilisateur fourni par le client ne permet de changer de
  collection cible.
- Le backend reste l'autorité des permissions et du masquage des prix.
- Les tests backend ciblés passent.
