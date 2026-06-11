# Validation finale et Docker

## Objectif

Valider l'ensemble de la fonctionnalité reset Bibliotheque après les
modifications backend, frontend et documentation.

## Périmètre

- Exécuter les tests backend.
- Exécuter le build frontend.
- Vérifier manuellement le scénario nominal :
  - connexion `ADMIN` ;
  - lancement du reset ;
  - réponse `202` ;
  - blocage d'un deuxième reset par `409` ;
  - réception ou simulation vérifiée du mail final.
- Vérifier le scénario import utilisateur pendant reset :
  - upload/analyze/import/configuration/reinit retournent `403`.
- Vérifier que les routes publiques Bibliotheque restent consultables.
- Rebuild Docker images si les changements impactent le runtime backend,
  frontend ou la configuration de déploiement.

## Commandes attendues

```bash
./test_backend.sh
cd frontend && npm run build
docker compose build
```

Adapter les commandes Docker au contexte du projet si un compose spécifique est
utilisé.

## Critères d'acceptation

- Tous les tests ciblés passent.
- Le build frontend passe.
- Les images Docker sont reconstruites si le runtime a changé.
- Le rapport final indique les fichiers de documentation vérifiés avec les
  marqueurs de conformité demandés par `AGENTS.md`.
