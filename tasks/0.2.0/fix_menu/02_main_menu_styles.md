# 02 - Homogénéisation visuelle des boutons du menu

## Objectif

Uniformiser les styles des boutons du menu principal avec une couleur proche de
la palette verte existante.

## Prérequis

- Lire `tasks/0.2.0/fix_menu/00_existing_code_analysis_result.md`.
- Terminer `01_main_menu_actions.md`.

## Étapes

1. Identifier les couleurs vertes déjà utilisées dans les styles frontend.
2. Adapter les classes CSS du menu dans les fichiers de styles existants.
3. Appliquer un style homogène à toutes les actions du menu.
4. Vérifier les états visuels :
   - normal ;
   - hover ;
   - focus ;
   - disabled ;
   - menu ouvert ;
   - affichage mobile.
5. Limiter l'impact aux boutons du menu sauf si une classe partagée existante
   impose une adaptation plus globale.

## Critères D'Acceptation

- Les boutons du menu ont un rendu homogène.
- Le style utilise une couleur cohérente avec la palette actuelle.
- Les états hover, focus et disabled sont lisibles.
- Le rendu mobile reste utilisable.
