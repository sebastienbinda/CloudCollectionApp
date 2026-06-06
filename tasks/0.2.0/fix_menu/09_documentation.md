# 09 - Documentation menu et layout commun

Statut : réalisée.

## Objectif

Mettre à jour les documentations associées après la migration du menu et du
layout commun.

Cette tâche doit être réalisée en dernier.

## Prérequis

- Terminer les tâches de développement frontend.
- Terminer les validations nécessaires.

## Documentation À Modifier

- `documentation/frontend-arch.md`
- `documentation/menu.md`
- `AGENTS.md`

## Documentation À Vérifier

- `documentation/site-plan.md`
- `documentation/authentication.md`
- `README.md`

## Étapes

1. Mettre à jour `documentation/frontend-arch.md` pour indiquer que toute
   nouvelle page React doit utiliser `PageLayout`.
2. Préciser dans `documentation/frontend-arch.md` que les pages ne doivent pas
   recréer leur propre header ou menu principal.
3. Mettre à jour `documentation/menu.md` pour documenter que le menu est porté
   par `PageLayout` sur toutes les pages.
4. Préciser dans `documentation/menu.md` que les actions du menu sont des
   boutons.
5. Préciser dans `documentation/menu.md` que `Connexion` ou `Deconnexion` est
   la dernière action du menu.
6. Mettre à jour `AGENTS.md` pour imposer l'utilisation de `PageLayout` lors de
   la création d'une nouvelle page.
7. Vérifier si `documentation/site-plan.md` doit être ajusté à cause du layout
   commun.
8. Vérifier si `documentation/authentication.md` doit être ajusté à cause de la
   présence du menu sur `/auth`.
9. Vérifier si `README.md` doit être mis à jour.
10. Lancer `git diff --check`.

## Critères D'Acceptation

- Les documentations concernées décrivent le layout commun.
- Les règles de création des nouvelles pages mentionnent `PageLayout`.
- Les règles du menu principal sont cohérentes avec l'implémentation.
- `README.md` est mis à jour si le comportement utilisateur, les routes, les
  commandes ou Docker changent.
- Le rapport final de conformité documentaire peut être produit avec les statuts
  🟢, 🟠 et 🔴 demandés par `AGENTS.md`.
