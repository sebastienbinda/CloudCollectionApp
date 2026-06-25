# Persistance des partages de collection

## Objectif

Ajouter le modèle SQL nécessaire pour conserver les partages créés par un
utilisateur sans stocker un token de partage brut.

## Périmètre

- Lire `documentation/database.md` avant toute modification.
- Ajouter une table de partage rattachée au propriétaire par son identifiant
  utilisateur.
- Persister au minimum : identifiant, propriétaire, date de création, date
  d'expiration, date de révocation nullable et permissions collection,
  wishlist et prix.
- Ajouter le modèle ORM dans un fichier dédié, la migration Alembic et le
  repository de lecture/écriture associé.
- Permettre de lister les partages actifs, expirés et révoqués sans supprimer
  les lignes expirées.
- Ajouter les index nécessaires à la validation par identifiant de partage et
  à la liste par propriétaire.
- Ne jamais persister le token HTTP brut. Le lien devra être reconstruit à
  partir des données persistées et signé par le backend.

## Hors périmètre

- Création des routes HTTP.
- Validation Bearer du profil `GUEST`.
- Interface frontend.

## Tests attendus

- Création et lecture d'un partage.
- Liste isolée par propriétaire.
- Révocation idempotente d'un partage appartenant au propriétaire.
- Conservation et identification d'un partage expiré.
- Migration et métadonnées ORM conformes.

## Critères d'acceptation

- Un partage possède toutes les informations nécessaires à sa validation et à
  son affichage.
- Aucun secret ou token brut n'est stocké en base.
- Les tests backend ciblés passent avec `./test_backend.sh`.
