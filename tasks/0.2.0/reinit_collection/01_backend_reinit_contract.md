# 01 - Contrat backend de réinitialisation

## Objectif

Ajouter le contrat HTTP du endpoint de réinitialisation de collection, sans
encore implémenter toute la persistance.

Cette tâche dépend de :

- `00_existing_code_analysis_and_contract.md`
- `00_existing_code_analysis_result.md`

## Endpoint

Créer ou étendre le contrôleur de collection utilisateur pour exposer :

```http
POST /api/users/collection/reinit
Authorization: Bearer <access_token>
```

## Autorisation

- Le endpoint doit exiger le profil `USER`.
- Le profil `ADMIN` ne doit pas être utilisé comme propriétaire frontend de
  collection.
- L'identifiant utilisateur doit être résolu depuis le token, jamais depuis une
  URL, une query string ou un body.

## Réponses

Réponses attendues :

- `200` : `{"reinitialized": true}`
- `404` : `{"error": "Collection introuvable."}`
- `500` : `{"error": "Unable to reinitialize collection."}`

Les erreurs ne doivent pas exposer de chemin disque interne, SQL, stack trace ou
détail sensible.

## Tests Backend

Ajouter des tests de route couvrant :

- accès sans token refusé ;
- succès `200` avec payload nominal ;
- absence de collection `404` ;
- erreur inattendue `500` ;
- résolution de l'utilisateur depuis le token.

## Contraintes

- Garder le contrôleur limité au mapping HTTP.
- Placer les décisions métier dans un service.
- Ne pas manipuler SQL ou fichier directement dans le contrôleur.
