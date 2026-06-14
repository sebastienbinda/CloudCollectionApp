# 09 - Documentation

## Objectif

Mettre à jour la documentation fonctionnelle et technique après
l'implémentation du référentiel plateformes applicatif.

Cette tâche est volontairement la dernière du découpage.

Elle doit s'appuyer sur :

- `task/0.2.6/plateforme_list/00_existing_code_analysis_result.md`
- toutes les tâches d'implémentation validées.

## Documentation À Mettre À Jour

Mettre à jour selon les changements réellement implémentés :

- `README.md` pour indiquer que la liste des plateformes est fournie par défaut
  par l'application ;
- `documentation/database.md` pour le schéma final de `t_platform`, ses
  contraintes et la stratégie de chargement ;
- `documentation/import.md` pour le nouveau fonctionnement d'import, le
  rattachement au référentiel, les seuils de matching, les warnings, les jeux
  non importés et l'email administrateur ;
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
rg -n "plateform|platforme|misent|recheche|aovir" documentation README.md task/0.2.6/plateforme_list
```

## Critères D'Acceptation

- La documentation reflète le comportement implémenté.
- Le README mentionne le référentiel de plateformes fourni par défaut.
- Les seuils de matching de plateformes sont documentés.
- Le contrat API est cohérent avec le backend.
- Le bilan final liste explicitement la conformité documentaire avec les
  marqueurs attendus par `AGENTS.md`.
