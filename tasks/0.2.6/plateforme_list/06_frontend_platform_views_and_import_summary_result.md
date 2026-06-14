# 06 - Résultat frontend plateformes et résumé d'import

## Résumé

La tâche 6 a été implémentée côté frontend.

## Changements Réalisés

- La liste publique Bibliothèque des plateformes n'affiche plus `status`.
- La liste publique Bibliothèque affiche maintenant `end_date` avec le libellé
  `Retrait`.
- Le tri frontend Bibliothèque plateformes accepte `end_date`.
- La configuration mobile de la table plateformes affiche `name` et `end_date`,
  afin de présenter le nom puis la date de retrait sur les écrans étroits.
- Les plateformes de collection normalisées côté frontend conservent les
  compteurs historiques et exposent aussi `release_date`, `end_date`,
  `manufacturer`, `description` et `total_games`.
- Les cartes plateformes de Ma collection affichent une ligne compacte
  `release_date / end_date`.
- Le résumé d'import affiche `linked_platforms` avec le libellé
  `Plateformes liees`.
- Le résumé d'import affiche les warnings `platform_matches` et
  `skipped_games`.

## Validations

- Build frontend :
  `npm run build`, statut `OK`.
- Rebuild Docker :
  `docker compose -f docker/docker-compose.yml build`, statut `OK`.

## Limites De Validation

- La validation visuelle via navigateur intégré n'a pas été lancée car
  `AGENTS.md` indique que `iab` n'est pas disponible dans ce workspace.

## Points Pour Les Tâches Suivantes

- La tâche 07 doit compléter la non-régression backend globale.
- La tâche 08 doit couvrir la validation runtime et Docker complète.
- La tâche 09 doit documenter les nouveaux champs API et le résumé d'import.
