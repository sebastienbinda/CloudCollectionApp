# 10 - Validation end-to-end Bibliotheque

## Objectif

Valider le workflow complet de consultation publique de la Bibliotheque.

## Etapes

1. Lancer les tests backend.
2. Lancer le build frontend.
3. Verifier les endpoints backend sans token :
   - `/api/library/entities` ;
   - `/api/library/platforms` ;
   - `/api/library/studios` ;
   - `/api/library/games`.
4. Verifier les endpoints avec recherche par `name`.
5. Verifier les endpoints avec pagination.
6. Verifier les endpoints avec tri simple et tri multiple.
7. Verifier les routes frontend sans utilisateur connecte.
8. Verifier les routes frontend avec utilisateur connecte.
9. Verifier que les pages ne proposent aucune action de modification.
10. Verifier que les donnees privees utilisateur ne sont jamais visibles.
11. Verifier que les composants partages n'ont pas casse accueil, plateforme et
    wishlist.
12. Rebuilder les images Docker si le comportement runtime est modifie.

## Criteres d'acceptation

- Les tests backend passent.
- Le build frontend passe.
- Les pages Bibliotheque sont accessibles publiquement.
- Les listes sont consultables, paginees, recherchables et triables.
- Le menu principal affiche Bibliotheque pour tous les visiteurs.
- Aucune donnee de collection privee n'est exposee.
- Accueil, detail plateforme et wishlist restent fonctionnels.

## Validation attendue

- `./test_backend.sh`
- `npm run build`
- Build Docker backend/frontend si necessaire.
