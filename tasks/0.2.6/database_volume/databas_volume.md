L'objectif de la tache est de pouvoir rendre configurable l'emplacement des données postggres sur l'hote du conteneur docker en env de production via une variable d'environement dans le .en en spécifiant le chemin aboslue.

## Résultat Branche `list_platform` - 2026-06-16

La tâche est réalisée.

Changements appliqués :

- `docker/docker-compose.online.yml` utilise désormais la variable
  `POSTGRES_DATA_HOST_DIR` pour monter le répertoire hôte PostgreSQL vers
  `/var/lib/postgresql/data`.
- `POSTGRES_DATA_HOST_DIR` est obligatoire en production et doit contenir un
  chemin absolu.
- `docker/.env.example` fournit un exemple :
  `/var/lib/cloudcollectionapp/postgres-data`.
- `README.md`, `documentation/ci.md` et `documentation/database.md` documentent
  la variable et la règle de persistance production.
- Le compose local conserve son volume nommé `postgres_data` pour ne pas
  modifier le workflow de développement.

Validations :

- `POSTGRES_DATA_HOST_DIR=/tmp/cloudcollectionapp-postgres-data docker compose -f docker/docker-compose.online.yml config --quiet` : OK.
- `docker compose -f docker/docker-compose.local.yml config --quiet` : OK.
- `git diff --check` : OK.
