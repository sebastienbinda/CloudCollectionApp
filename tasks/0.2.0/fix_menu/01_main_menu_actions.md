# 01 - Correction des actions du menu principal

## Objectif

Rendre les entrées du menu principal homogènes et conformes à la tâche
`fix_menu`.

## Prérequis

- Lire `tasks/0.2.0/fix_menu/00_existing_code_analysis_result.md`.
- Lire `documentation/menu.md`.

## Étapes

1. Modifier `frontend/src/components/MainMenu.jsx`.
2. Remplacer l'entrée `Connexion` en lien HTML par un composant `button`.
3. Vérifier que toutes les entrées du menu sont des boutons.
4. Placer l'action `Connexion` ou `Deconnexion` en dernière position de la
   liste.
5. Conserver les entrées indisponibles en `disabled`.
6. Préserver les comportements existants :
   - ouverture et fermeture au clic ;
   - fermeture au clic extérieur ;
   - fermeture avec `Escape` ;
   - fermeture après une action ;
   - fermeture au pointer leave uniquement pour la souris ;
   - compatibilité tactile.
7. Conserver `aria-expanded` et `aria-haspopup` sur le bouton déclencheur.

## Critères D'Acceptation

- Aucune entrée du menu n'est rendue avec un lien HTML.
- `Connexion` ou `Deconnexion` est la dernière action visible du menu.
- Les règles d'accessibilité et de fermeture du menu restent respectées.
- Les règles de navigation et d'accès ne changent pas.
