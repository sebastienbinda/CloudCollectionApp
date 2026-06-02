# 07 - Documentation et validation

## Objectif

Mettre à jour la documentation fonctionnelle et technique, puis valider
l'ensemble du périmètre import wishlist.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.0/import_wishlist/00_existing_code_analysis_result.md`
- `tasks/0.2.0/import_wishlist/import_wishlist.md`

## Documentation À Mettre À Jour

Mettre à jour selon les changements réellement implémentés :

- `README.md` si les commandes, routes, comportements utilisateur ou Docker
  changent ;
- `documentation/import.md` pour le nouveau workflow, les modes wishlist et
  l'écran de résumé post-import ;
- `documentation/backend-api.md` pour les contrats `POST /api/users/import`,
  `GET /collections/videogames` et
  `GET /collections/videogames/games/search` ;
- `documentation/site-plan.md` pour le comportement post-import ;
- `documentation/frontend-arch.md` si l'orchestration frontend change ;
- `documentation/backend-arch.md` si les responsabilités backend évoluent ;
- `documentation/database.md` pour la colonne `t_user_collection.wishlist` ;
- créer `documentation/collection.md` pour documenter la consultation de la
  collection utilisateur si cette documentation manque toujours.

## Validation Backend

Lancer :

```bash
./test_backend.sh
```

Vérifier que les tests couvrent :

- contrat wishlist ;
- migration et persistance ;
- import wishlist ;
- statistiques et recherche collection.

## Validation Frontend

Lancer depuis `frontend/` :

```bash
npm run build
```

Vérifier manuellement ou par tests disponibles :

- workflow import ;
- écran de résumé ;
- lien vers collection ;
- page collection filtrée sur `wishlist=false`.

## Validation Docker

Rebuild les images concernées si les changements impactent le runtime backend ou
frontend :

```bash
docker compose -f docker/docker-compose.local.yml build backend web
```

## Vérifications Finales

Lancer :

```bash
git diff --check
rg -n "whishlist|wihslist|whislist" .
```

Vérifier :

- aucun nom technique mal orthographié ;
- les docs sont cohérentes entre elles ;
- les règles de chaque `documentation/*.md` concerné sont respectées ;
- le README a été vérifié et mis à jour si nécessaire.

## Critères D'Acceptation

- La documentation reflète le comportement implémenté.
- `documentation/collection.md` existe si demandé par la tâche chapeau.
- Les tests backend passent.
- Le build frontend passe.
- Les images Docker concernées sont reconstruites si nécessaire.
- Le bilan final liste explicitement la conformité documentaire avec les
  marqueurs attendus par `AGENTS.md`.
