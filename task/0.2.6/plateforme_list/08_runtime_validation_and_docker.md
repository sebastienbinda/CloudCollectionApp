# 08 - Validation runtime et Docker

## Objectif

Valider que les changements backend et frontend fonctionnent ensemble et
reconstruire les images si le comportement runtime est impacté.

Cette tâche doit s'appuyer sur :

- `task/0.2.6/plateforme_list/00_existing_code_analysis_result.md`
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
- liste Bibliothèque des plateformes ;
- import avec plateforme connue ;
- import avec plateforme contenant une coquille ;
- import avec score entre 25% et 75% et email administrateur ;
- import refusé pour un jeu avec score inférieur à 25% ;
- import avec seuils personnalisés via `.env` ;
- warnings visibles ;
- email administrateur déclenché dans le cas prévu ;
- résumé d'import avec plateformes liées.

## Critères D'Acceptation

- Les validations backend et frontend sont exécutées.
- Les images Docker sont reconstruites si nécessaire.
- Les limitations ou échecs non liés sont documentés.
