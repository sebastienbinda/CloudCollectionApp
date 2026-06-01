# 05 - Documentation et validation finale

## Objectif

Finaliser la documentation et valider l'ensemble de l'import configurable.

Cette tâche dépend de toutes les tâches précédentes.

## Documentation À Mettre À Jour

Mettre à jour :

- `documentation/import.md`
- `documentation/backend-api.md` si le contrat API détaillé change ;
- `documentation/backend-arch.md` si l'architecture des readers est ajoutée ;
- `documentation/frontend-arch.md` si l'onboarding ou les hooks changent ;
- `documentation/database.md` uniquement si le contrat
  `collection_file_description` doit être précisé ;
- `README.md` si le comportement utilisateur, les commandes ou la configuration
  changent.

`documentation/import.md` doit expliquer :

- le nouveau fonctionnement configurable ;
- le contrat `multipart/form-data` ;
- le champ `collection_file_description` ;
- les trois modes de configuration ;
- les erreurs `422` ;
- l'interface générique `CollectionFileReader` ;
- la factory par `file_type` ;
- l'objectif de supporter plusieurs types de fichiers.

## Recherches À Effectuer

Vérifier qu'il ne reste pas d'ancien import à structure fixe hors tests
explicitement conservés :

```bash
rg -n "header=5|usecols=\"F:M\"|Liste de souhaits|Accueil" backend documentation frontend/src
```

Adapter la recherche selon les noms réellement utilisés pendant le
développement.

## Validations

Lancer :

```bash
./test_backend.sh
cd frontend && npm run build
git diff --check
```

Rebuild Docker si le runtime backend, frontend ou Nginx change :

```bash
docker compose -f docker/docker-compose.local.yml build backend web
```

## Critères D'Acceptation

- La documentation décrit le nouveau contrat.
- Les validations backend passent.
- Le build frontend passe.
- `git diff --check` passe.
- Les images Docker concernées sont reconstruites si nécessaire.
- Le bilan final mentionne les éventuels écarts avec le rapport d'analyse de la
  tâche `00`.
