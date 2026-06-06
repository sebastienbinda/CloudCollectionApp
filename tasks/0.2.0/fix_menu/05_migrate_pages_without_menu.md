# 05 - Migration des pages sans menu commun

## Objectif

Rendre le menu principal accessible sur les pages qui n'utilisent pas encore le
menu commun.

## Prérequis

- Terminer `03_page_layout_component.md`.
- Lire `tasks/0.2.0/fix_menu/00_existing_code_analysis_result.md`.
- Lire `documentation/site-plan.md`.

## Pages Cibles Probables

- `AuthView`
- `AdminDashboardView`
- `UsersView`
- `AddGameView`
- `PlatformDetailView`

La liste exacte doit venir du rapport d'analyse.

## Étapes

1. Migrer les pages ciblées vers `PageLayout`.
2. Ajouter les props session et navigation nécessaires.
3. Intégrer ou remplacer les boutons retour locaux sans perdre les actions
   contextuelles existantes.
4. Vérifier que `/auth` reste utilisable sans session.
5. Vérifier que les pages privées et admin gardent leurs contraintes d'accès.
6. Ne pas modifier les règles de routage ou d'autorisation.

## Critères D'Acceptation

- Toutes les pages ciblées exposent le menu principal.
- Les actions contextuelles existantes restent disponibles.
- Les routes publiques, privées et admin respectent `documentation/site-plan.md`.
- Aucune logique métier n'est déplacée dans les composants de layout.
