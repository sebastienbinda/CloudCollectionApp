# 04 - Migration des pages utilisant déjà MainMenu

## Objectif

Migrer les pages qui utilisent déjà `MainMenu` vers `PageLayout`.

## Prérequis

- Terminer `03_page_layout_component.md`.
- Lire `tasks/0.2.0/fix_menu/00_existing_code_analysis_result.md`.

## Pages Cibles Probables

- `AboutView`
- `HomeView`
- `LibraryHomeView`
- `LibraryEntityListView`
- `UserCollectionOnboardingView`

La liste exacte doit venir du rapport d'analyse.

## Étapes

1. Remplacer les headers locaux par `PageLayout`.
2. Reprendre les textes, titres, sous-titres, images et contenus de header
   existants.
3. Conserver les classes spécifiques utiles à chaque page.
4. Supprimer les imports directs de `MainMenu` devenus inutiles.
5. Vérifier que le menu reste accessible sur chaque page migrée.

## Critères D'Acceptation

- Les pages ciblées utilisent `PageLayout`.
- Le rendu fonctionnel des pages reste équivalent.
- Les règles de menu de `documentation/menu.md` restent respectées.
- Les routes publiques restent publiques.
