# 09 - Documentation

## Objectif

Mettre à jour la documentation fonctionnelle et technique après
l'implémentation du référentiel plateformes applicatif.

Cette tâche est volontairement la dernière du découpage.

Elle doit s'appuyer sur :

- `tasks/0.2.6/plateforme_list/00_existing_code_analysis_result.md`
- toutes les tâches d'implémentation validées.

## Documentation À Mettre À Jour

Mettre à jour selon les changements réellement implémentés :

- `README.md` pour indiquer que la liste des plateformes est fournie par défaut
  par l'application ;
- `documentation/database.md` pour le schéma final de `t_platform`, ses
  contraintes, la stratégie de chargement et la preservation du référentiel lors
  des resets/réinitialisations ;
- `documentation/backend-arch.md` pour préciser que le seed du catalogue
  plateformes est rejoué au démarrage de manière idempotente après Alembic ;
- `documentation/import.md` pour le nouveau fonctionnement d'import, le
  rattachement au référentiel, les seuils de matching, les warnings, les jeux
  non importés et l'email administrateur ;
- `documentation/backend-arch.md` pour le cache serveur du catalogue plateformes
  partagé entre imports et recherche, avec expiration toutes les 5 heures ;
- `README.md` et les fichiers Docker si les variables
  `MATCHING_LOW_LVL_RATING` et `MATCHING_HIGH_LEVEL_RATING` doivent être
  exposées dans les environnements local ou online ;
- `documentation/backend-api.md` pour les formats d'import et de plateformes ;
- `documentation/backend-arch.md` si de nouveaux services backend structurants
  sont ajoutés ;
- `documentation/frontend-arch.md` si l'organisation des hooks/services
  frontend change ;
- `documentation/site-plan.md` si le comportement ou le rendu des pages change.

## Vérification README

Après chaque modification de code réalisée dans les tâches précédentes,
vérifier si `README.md` doit être mis à jour pour :

- comportement utilisateur ;
- routes ;
- configuration `.env` ;
- seuils `MATCHING_LOW_LVL_RATING` et `MATCHING_HIGH_LEVEL_RATING` ;
- commandes ;
- Docker ;
- tests ;
- changement de contrat d'import.

## Validation Finale

Lancer ou vérifier que les validations de la tâche `08` ont été exécutées.

Vérifier aussi :

```bash
git diff --check
rg -n "plateform|platforme|misent|recheche|aovir" documentation README.md tasks/0.2.6/plateforme_list
```

## Critères D'Acceptation

- La documentation reflète le comportement implémenté.
- Le README mentionne le référentiel de plateformes fourni par défaut.
- Les seuils de matching de plateformes sont documentés.
- Le contrat API est cohérent avec le backend.
- Le bilan final liste explicitement la conformité documentaire avec les
  marqueurs attendus par `AGENTS.md`.

## Résultat Branche `list_platform` - 2026-06-16

Documentation mise à jour :

- `README.md` mentionne le référentiel plateformes et alias fourni par défaut,
  ainsi que les seuils `MATCHING_LOW_LVL_RATING` et
  `MATCHING_HIGH_LEVEL_RATING`.
- `documentation/database.md` décrit le schéma final de `t_platform`,
  `t_platform_alias`, le seed idempotent depuis `backend/resources`, la
  synchronisation admin et la préservation du référentiel lors des resets et
  réinitialisations.
- `documentation/backend-api.md` documente le format plateformes avec
  `end_date`, sans `status`, le tri `end_date`, le compteur
  `linked_platforms`, les warnings de matching et la route admin
  `POST /api/library/platform-catalog/sync`.
- `documentation/import.md` décrit le rattachement au référentiel, les alias,
  les seuils configurables, les jeux importés avec vérification manuelle, les
  jeux ignorés et le rapport email administrateur.
- `documentation/backend-arch.md` décrit les services de seed/synchronisation
  du catalogue et le cache serveur plateformes partagé avec TTL cinq heures.
- `documentation/frontend-arch.md` décrit les actions admin Bibliothèque
  déclenchées depuis Configuration via hooks et service dédiés.
- `documentation/site-plan.md` décrit l'action admin Configuration de mise à
  jour du catalogue plateformes, la page publique de détail plateforme
  Bibliothèque et la route de détail plateforme de collection.
- `documentation/bibliotheque.md` liste la page publique
  `/bibliotheque/plateformes/<platform_id>` et l'endpoint
  `GET /api/library/platforms/<platform_id>`.
- `documentation/authentication.md` décrit la séparation `USER` / `ADMIN` pour
  les routes d'administration Bibliothèque.
- `docker/.env.example`, `docker/docker-compose.local.yml` et
  `docker/docker-compose.online.yml` exposent les seuils de matching au backend.

Validations réalisées pour cette tâche :

- `git diff --check` : OK.
- `rg -n "plateform|platforme|misent|recheche|aovir" documentation README.md tasks/0.2.6/plateforme_list/09_documentation.md` :
  exécuté. Les occurrences restantes de `plateform` correspondent au mot
  français valide `plateforme` ou à des chemins de tâche.
- `docker compose -f docker/docker-compose.local.yml config --quiet` : OK.
- `docker compose -f docker/docker-compose.online.yml config --quiet` : OK.

Validations héritées des tâches précédentes et conservées comme référence :

- `./test_backend.sh` : OK, 402 tests.
- `npm run build` depuis `frontend/` : OK.
- `docker compose -f docker/docker-compose.local.yml build backend web` : OK.
