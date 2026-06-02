# 05 - Workflow frontend import wishlist

## Objectif

Adapter l'onboarding frontend d'import pour configurer la wishlist, exploiter le
retour d'import et afficher un écran de résumé après succès.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.0/import_wishlist/00_existing_code_analysis_result.md`
- `tasks/0.2.0/import_wishlist/import_wishlist.md`

## Périmètre Frontend

Modifier les fichiers désignés par le rapport pour :

- afficher uniquement l'upload et le type de fichier avant analyse ;
- afficher le reste du formulaire après analyse ;
- préremplir `header_row` avec la première ligne de la plage saisie ;
- préremplir les mappings avec les colonnes de la plage ;
- ajouter une section wishlist avant la sélection des plages collection ;
- gérer les modes `none`, `sheet` et `column` ;
- réutiliser un composant commun pour configurer une plage et un mapping ;
- envoyer le contrat JSON wishlist validé ;
- afficher un écran de résumé après succès d'import ;
- proposer un lien vers la page collection au lieu de rediriger automatiquement.

## Règles D'Architecture

- Garder l'orchestration dans `frontend/src/hooks/collection/`.
- Garder les appels HTTP dans `frontend/src/services/`.
- Garder les composants centrés sur l'affichage et les interactions.
- Ne pas dupliquer les validations métier backend côté frontend.
- Utiliser le backend availability guard pour les appels automatiques.

## Tests Ou Validations Attendues

Ajouter ou modifier les tests disponibles, ou documenter la validation manuelle
si le projet n'a pas de tests frontend adaptés :

- état initial avant analyse ;
- affichage du formulaire après analyse ;
- configuration mode `none` ;
- configuration mode `sheet` ;
- configuration mode `column` ;
- payload envoyé au backend ;
- écran de résumé post-import ;
- lien vers `/collection`.

## Critères D'Acceptation

- Le workflow frontend produit un JSON conforme au contrat backend.
- Le succès d'import n'entraîne plus de redirection automatique vers
  `/collection`.
- L'écran de résumé affiche les compteurs retournés par le backend.
- Le build frontend passe.
