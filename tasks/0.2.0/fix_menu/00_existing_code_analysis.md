# 00 - Analyse du code existant

## Objectif

Analyser les pages, composants, props de navigation et styles existants avant
de modifier le menu et le layout commun.

Cette tâche ne doit pas modifier le code applicatif.

## Documentation À Lire

- `tasks/0.2.0/fix_menu/fix_menu.md`
- `documentation/menu.md`
- `documentation/frontend-arch.md`
- `documentation/site-plan.md`
- `documentation/authentication.md` si la page d'authentification ou la session
  sont modifiées

## Analyse Frontend

Identifier et documenter :

- toutes les pages React existantes dans `frontend/src/components/` ;
- les pages qui utilisent déjà `MainMenu` ;
- les pages qui ont un header local ;
- les pages qui ont un bouton retour local ;
- les pages qui n'exposent pas encore le menu ;
- les props de session et de navigation nécessaires pour utiliser le menu sur
  toutes les pages ;
- les classes CSS existantes liées au menu, aux headers, aux boutons, au footer
  et aux containers de page ;
- les éventuels risques sur les routes publiques, privées et admin.

## Livrable

Créer le fichier :

```text
tasks/0.2.0/fix_menu/00_existing_code_analysis_result.md
```

Le rapport doit contenir :

- la liste des pages à migrer ;
- les props manquantes par page ;
- les composants à créer ou modifier ;
- les styles à réutiliser ou adapter ;
- les risques identifiés ;
- la stratégie de migration proposée.

## Critères D'Acceptation

- Le rapport existe.
- Le rapport donne assez d'information pour réaliser les sous-tâches suivantes
  sans nouvelle exploration générale.
- Les documentations concernées ont été lues.
- Aucune modification fonctionnelle n'est réalisée pendant cette tâche.
