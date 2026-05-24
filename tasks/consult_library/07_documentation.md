# 07 - Documentation Bibliothèque

## Objectif

Documenter la fonctionnalité Bibliothèque et mettre à jour les documentations impactées.

## Étapes

1. Créer `documentation/bibliotheque.md`.
2. Décrire les règles fonctionnelles :
   - accès public ;
   - lecture seule ;
   - base globale ;
   - absence de données privées utilisateur.
3. Décrire les routes frontend.
4. Décrire les endpoints backend et leurs paramètres.
5. Mettre à jour `documentation/site-plan.md`.
6. Mettre à jour `documentation/backend-api.md`.
7. Mettre à jour `documentation/frontend-arch.md` si de nouveaux hooks, services ou règles frontend sont ajoutés.
8. Mettre à jour `documentation/backend-arch.md` si un nouveau contrôleur, service ou repository est ajouté.
9. Vérifier si `README.md` doit être mis à jour.

## Critères d'acceptation

- `documentation/bibliotheque.md` existe et synthétise les règles à préserver.
- `documentation/site-plan.md` liste les nouvelles routes publiques.
- `documentation/backend-api.md` décrit les nouveaux endpoints.
- Les documentations d'architecture restent cohérentes avec l'implémentation.

## Validation attendue

- Relire les documentations concernées.
- Lancer `git diff --check`.
