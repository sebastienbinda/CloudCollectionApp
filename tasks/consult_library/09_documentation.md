# 09 - Documentation Bibliotheque

## Objectif

Documenter la fonctionnalite Bibliotheque et mettre a jour les documentations
impactees.

## Etapes

1. Creer `documentation/bibliotheque.md`.
2. Decrire les regles fonctionnelles :
   - acces public ;
   - lecture seule ;
   - base globale ;
   - absence de donnees privees utilisateur.
3. Decrire les routes frontend.
4. Decrire les endpoints backend et leurs parametres.
5. Mettre a jour `documentation/site-plan.md`.
6. Mettre a jour `documentation/backend-api.md`.
7. Mettre a jour `documentation/frontend-arch.md` si de nouveaux hooks,
   services ou composants partages sont ajoutes.
8. Mettre a jour `documentation/backend-arch.md` si un nouveau controleur,
   service ou repository est ajoute.
9. Mettre a jour `documentation/menu.md` si l'entree Bibliotheque modifie les
   regles du menu principal.
10. Verifier si `README.md` doit etre mis a jour.

## Criteres d'acceptation

- `documentation/bibliotheque.md` existe et synthetise les regles a preserver.
- `documentation/site-plan.md` liste les nouvelles routes publiques.
- `documentation/backend-api.md` decrit les nouveaux endpoints.
- Les documentations d'architecture restent coherentes avec l'implementation.

## Validation attendue

- Relire les documentations concernees.
- Lancer `git diff --check`.
