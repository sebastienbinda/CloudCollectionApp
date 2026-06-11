# Action frontend admin dans Configuration

## Objectif

Ajouter dans la page Configuration une action visible uniquement par les profils
`ADMIN` pour lancer le reset Bibliotheque.

## Périmètre

- Lire et respecter `documentation/frontend-arch.md`,
  `documentation/site-plan.md`, `documentation/menu.md` et
  `documentation/bibliotheque.md`.
- Ajouter un service frontend pour appeler `POST /api/library/reset`.
- Ajouter un hook dédié si nécessaire, selon l'architecture existante.
- Ajouter un encart visible uniquement pour `ADMIN`.
- Demander confirmation avant l'appel, avec un message très visible sur le
  risque de destruction/reconstruction de la Bibliotheque.
- Après `202`, afficher un message indiquant que le reset est en cours et que le
  résultat sera envoyé par email.
- Après `409`, afficher un message indiquant qu'un reset est déjà en cours.
- Afficher clairement les erreurs backend inattendues.

## Hors périmètre

- Endpoint de statut du job.
- Polling frontend.
- Modification des pages publiques Bibliotheque.

## Tests et validation attendus

- Vérifier que l'encart n'apparaît pas pour `USER`.
- Vérifier que l'encart apparaît pour `ADMIN`.
- Vérifier les messages `202` et `409`.
- Exécuter le build frontend.

## Critères d'acceptation

- La page Configuration conserve le layout partagé existant.
- Le frontend ne contient pas de logique métier de reset.
- Les règles de `documentation/site-plan.md` sont respectées pour chaque page
  concernée.
