# 03 - Création du composant PageLayout

## Objectif

Créer un composant React commun pour structurer toutes les pages avec un header,
le menu principal, les informations de page, le footer et le contenu.

## Prérequis

- Lire `tasks/0.2.0/fix_menu/00_existing_code_analysis_result.md`.
- Lire `documentation/frontend-arch.md`.
- Lire `documentation/menu.md`.

## Étapes

1. Créer `frontend/src/components/PageLayout.jsx`.
2. Ajouter l'en-tête de fichier obligatoire.
3. Ajouter les commentaires publics en français.
4. Intégrer `MainMenu`.
5. Intégrer `AppFooter` dans `PageLayout`.
6. Prévoir des props explicites pour :
   - le titre ;
   - l'eyebrow ;
   - le sous-titre ;
   - les classes spécifiques de shell et header ;
   - un contenu de header optionnel ;
   - le contenu principal ;
   - les informations de session ;
   - les callbacks de navigation du menu.
7. Retirer `AppFrame` de `frontend/src/App.jsx`.
8. Supprimer `frontend/src/components/AppFrame.jsx` après la migration vers
   `PageLayout`.
9. Préserver la responsabilité des pages : affichage et interactions seulement.

## Critères D'Acceptation

- `PageLayout.jsx` existe.
- Le composant contient le header, le menu, les informations de page, le footer
  et le contenu.
- `App.jsx` ne dépend plus de `AppFrame`.
- `frontend/src/components/AppFrame.jsx` est supprimé.
- Les props sont explicites.
- Le composant ne contient pas de logique métier.
- Le fichier respecte les règles de taille et de documentation du projet.
