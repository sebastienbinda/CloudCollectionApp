# 08 - Validation runtime et Docker

## Objectif

Valider que les changements backend et frontend fonctionnent ensemble et
reconstruire les images si le comportement runtime est impacté.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.6/plateforme_list/00_existing_code_analysis_result.md`
- toutes les tâches d'implémentation précédentes.

## Validations À Exécuter

- Lancer les tests backend :

```bash
./test_backend.sh
```

- Lancer le build frontend depuis `frontend/` :

```bash
npm run build
```

- Vérifier les incohérences de diff :

```bash
git diff --check
```

- Rebuilder les images concernées si les changements touchent le runtime :

```bash
docker compose -f docker/docker-compose.local.yml build backend web
```

## Vérifications Fonctionnelles

Vérifier au minimum :

- base vide initialisée avec les plateformes du CSV ;
- `t_platform` vidée puis repeuplée au redémarrage applicatif par le seed
  idempotent ;
- liste Bibliothèque des plateformes ;
- import avec plateforme connue ;
- import avec plateforme contenant une coquille ;
- import avec score entre 25% et 75% et email administrateur ;
- import refusé pour un jeu avec score inférieur à 25% ;
- import avec seuils personnalisés via `.env` ;
- warnings visibles ;
- email administrateur déclenché dans le cas prévu ;
- résumé d'import avec plateformes liées ;
- preservation de `t_platform` après reset Bibliothèque admin ;
- preservation de `t_platform` après réinitialisation collection utilisateur.

## Critères D'Acceptation

- Les validations backend et frontend sont exécutées.
- Les images Docker sont reconstruites si nécessaire.
- Les limitations ou échecs non liés sont documentés.

## Résultat Branche `list_platform` - 2026-06-16

Validations exécutées :

- `./test_backend.sh` : OK, 396 tests passés.
- `npm run build` depuis `frontend/` : OK, build Vite réussi.
- `git diff --check` : OK, aucune incohérence de diff détectée.
- `docker compose -f docker/docker-compose.local.yml build backend web` : OK,
  images `cloudcollectionapp-backend` et `cloudcollectionapp-web` reconstruites.
- `docker compose -f docker/docker-compose.local.yml up -d backend web` : OK,
  conteneurs recréés avec les images reconstruites.

Vérifications runtime non destructives exécutées :

- `docker compose -f docker/docker-compose.local.yml ps` : services
  `database`, `backend`, `web` et `mailpit` démarrés, base PostgreSQL healthy.
- SQL `select count(*) from cloudcollectionapp.t_platform;` dans le conteneur
  `database` : 226 plateformes présentes.
- Requête interne depuis le conteneur `web` vers
  `http://127.0.0.1:80/api/library/platforms?size=5` : HTTP 200, payload
  paginé avec `totalElements=226`.
- Requête interne depuis le conteneur `web` vers `http://127.0.0.1:80/` :
  HTML frontend servi avec les assets buildés.
- Logs backend : démarrage Gunicorn OK, Alembic exécuté, schéma PostgreSQL
  initialisé.
- Logs web : Nginx démarré, requête `/api/library/platforms?size=5` servie en
  HTTP 200.

Couverture des vérifications fonctionnelles :

- Les scénarios d'import avec plateforme connue, coquille acceptée, score entre
  25% et 75%, score inférieur à 25%, score nul, seuils personnalisés, warnings,
  email administrateur, compteur de plateformes liées, conservation de
  `t_platform` après reset Bibliothèque et conservation de `t_platform` après
  réinitialisation collection utilisateur sont couverts par les tests backend
  validés dans la tâche `07`.
- La vérification de base vide et le vidage/repeuplement volontaire de
  `t_platform` n'ont pas été rejoués de façon destructive sur la stack locale
  existante. La validation runtime s'est limitée à des sondes non destructives
  sur la base active et aux tests automatisés du seed idempotent.

Limites :

- L'accès HTTP host vers `localhost:8080` a échoué depuis le sandbox Codex
  (`curl: Failed to connect`). Le port est pourtant publié par Docker Compose ;
  les sondes équivalentes exécutées depuis le conteneur `web` ont validé Nginx,
  le frontend statique et le proxy backend.
- L'`iab` intégré n'est pas disponible dans ce workspace, conformément à
  `AGENTS.md`; aucune validation visuelle navigateur n'a donc été exécutée.
