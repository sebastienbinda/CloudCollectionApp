# 05 - Documentation et validation

## Objectif

Mettre à jour la documentation fonctionnelle et technique, puis valider le
périmètre frontend de consultation wishlist.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.0/user_wishlist_view/00_existing_code_analysis_result.md`
- `tasks/0.2.0/user_wishlist_view/user_wishlist_view.md`

## Documentation À Mettre À Jour

Mettre à jour selon les changements réellement implémentés :

- `documentation/collection.md` pour la consultation de la wishlist via
  `wishlist=true` ;
- `documentation/site-plan.md` pour la route privée `/wishlist` ;
- `documentation/menu.md` pour l'entrée `Liste de souhaits` ;
- `documentation/frontend-arch.md` après confirmation, pour documenter que les
  tris de listes backend doivent être demandés au backend et non recalculés côté
  React ;
- `documentation/backend-arch.md` après confirmation, pour documenter que le
  backend est responsable de l'ordre de retour des endpoints exposant `sort` ;
- `documentation/backend-api.md` uniquement si la documentation du filtre ou du
  tri wishlist existant doit être clarifiée ;
- `README.md` si le comportement utilisateur, les routes ou les commandes
  documentées changent.

Ne pas modifier une règle documentaire existante de manière contradictoire sans
confirmation explicite.

## Validation Frontend

Lancer depuis `frontend/` :

```bash
npm run build
```

Vérifier que le build couvre :

- la nouvelle route `/wishlist` ;
- l'entrée de menu ;
- les composants partagés ;
- le chargement wishlist ;
- les tris demandés au backend.

## Validation Backend

Aucun changement backend n'est attendu.

Si une modification backend a malgré tout été nécessaire, lancer :

```bash
./test_backend.sh
```

et expliquer pourquoi le backend a été modifié malgré la tâche chapeau.

## Validation Docker

Rebuild l'image frontend si les changements impactent le runtime web :

```bash
docker compose -f docker/docker-compose.local.yml build web
```

Rebuild l'image backend uniquement si un changement backend a été réalisé.

## Vérifications Finales

Lancer :

```bash
git diff --check
rg -n "whishlist|wihslist|whislist|spécifoque|éccrans" .
```

Vérifier :

- aucun nom technique wishlist mal orthographié ;
- aucune route backend wishlist dédiée n'a été créée ;
- la page collection conserve `wishlist=false` ;
- la page wishlist utilise `wishlist=true` ;
- les tris de consultation sont demandés au backend ;
- les docs sont cohérentes entre elles ;
- le README a été vérifié et mis à jour si nécessaire.

## Critères D'Acceptation

- La documentation reflète le comportement implémenté.
- `npm run build` passe.
- Les tests backend passent si le backend a été modifié.
- Les images Docker concernées sont reconstruites si nécessaire.
- Le bilan final liste explicitement la conformité documentaire avec les
  marqueurs attendus par `AGENTS.md`.
