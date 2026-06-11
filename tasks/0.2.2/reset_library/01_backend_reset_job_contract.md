# Contrat backend du job de reset

## Objectif

Ajouter le contrat HTTP et l'infrastructure de lancement du job asynchrone de
reset Bibliotheque.

## Périmètre

- Ajouter `POST /api/library/reset`.
- Protéger l'endpoint par Bearer token avec profil `ADMIN` uniquement.
- Retourner `202 Accepted` avec le payload :

```json
{
  "job_id": 25
}
```

- Retourner `409 Conflict` si un reset est déjà en cours.
- Ne pas ajouter d'endpoint de statut.
- Introduire un registre ou coordinateur de job en mémoire, avec identifiant de
  job, état d'exécution minimal et verrou de concurrence.
- S'assurer que `/api/routes` expose correctement l'authentification et le
  profil `ADMIN` pour cette route.

## Hors périmètre

- Le clean complet de la base.
- La réimportation effective des collections.
- Le frontend.
- L'envoi du mail final.

## Tests attendus

- Accès refusé sans token.
- Accès refusé pour un profil `USER`.
- Accès accepté pour `ADMIN` avec `202` et `job_id`.
- Deuxième appel pendant un reset retournant `409`.
- Métadonnées `/api/routes` conformes.

## Critères d'acceptation

- Le lancement du job ne bloque pas la réponse HTTP.
- Un seul reset peut être lancé à la fois.
- Les tests backend ciblés passent.
