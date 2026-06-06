# 07 - Validation frontend

## Objectif

Valider que les modifications du menu et du layout commun ne cassent pas
l'application frontend.

## Prérequis

- Terminer les tâches de développement frontend.

## Étapes

1. Lancer `npm run build` depuis `frontend/`.
2. Vérifier le menu en desktop :
   - fermé ;
   - ouvert ;
   - actions disponibles ;
   - actions disabled.
3. Vérifier le menu en mobile.
4. Vérifier les routes publiques :
   - `/about` ;
   - `/auth` ;
   - `/bibliotheque` ;
   - `/bibliotheque/plateformes` ;
   - `/bibliotheque/studios` ;
   - `/bibliotheque/jeux`.
5. Vérifier les routes privées et admin si une session de test est disponible.
6. Lancer `git diff --check`.

## Critères D'Acceptation

- `npm run build` réussit.
- Le menu fonctionne en desktop et mobile.
- Les routes publiques restent accessibles sans session.
- Les routes privées restent protégées.
- Aucun problème de whitespace n'est détecté par `git diff --check`.
