# 06 - Frontend plateformes et résumé d'import

## Objectif

Adapter les écrans frontend qui affichent les plateformes et le résumé d'import
au nouveau contrat backend.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.6/plateforme_list/00_existing_code_analysis_result.md`
- `tasks/0.2.6/plateforme_list/04_backend_import_result_contract.md`
- `tasks/0.2.6/plateforme_list/05_backend_platform_api_format.md`
- `documentation/frontend-arch.md`
- `documentation/site-plan.md`

## Frontend À Modifier

Selon les noms confirmés dans le rapport d'analyse :

- services API plateformes ;
- hooks de plateformes ;
- écran de liste des plateformes Bibliothèque ;
- écran ou composants de détail / collection par plateforme si concernés ;
- recherche des plateformes de collection, qui reçoit désormais aussi
  `release_date`, `end_date`, `manufacturer`, `description` et `total_games`
  tout en conservant les compteurs collection historiques ;
- résumé post-import ;
- styles responsive.

## Règles D'Affichage

- Les écrans ne doivent plus dépendre des colonnes supprimées.
- Les plateformes doivent afficher les nouvelles colonnes disponibles.
- Les compteurs collection existants (`nb_games`, `total_value`,
  `average_value`) peuvent rester utilisés dans les écrans collection, mais
  `total_games` devient le compteur catalogue standard quand il est disponible.
- En mobile, chaque encart de plateforme doit afficher :
  - première ligne : nom ;
  - deuxième ligne : `release_date / end_date`.
- Le résumé d'import doit afficher le nombre de plateformes liées à l'import,
  pas le nombre de plateformes créées.
- Les warnings de plateformes incertaines doivent rester visibles pour
  l'utilisateur.

## Validations Attendues

- Lancer le build frontend.
- Vérifier que les textes ne débordent pas sur mobile.
- Ne pas utiliser le navigateur intégré `iab`, conformément à `AGENTS.md`, sauf
  si l'utilisateur confirme qu'il est restauré.

## Critères D'Acceptation

- Le frontend compile.
- Les listes de plateformes consomment le nouveau format.
- Le rendu mobile respecte la règle demandée.
- Le résumé d'import reflète le nouveau compteur backend.
