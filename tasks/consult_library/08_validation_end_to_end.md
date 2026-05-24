# 08 - Validation end-to-end Bibliothèque

## Objectif

Valider le workflow complet de consultation publique de la Bibliothèque.

## Étapes

1. Lancer les tests backend.
2. Lancer le build frontend.
3. Vérifier les endpoints backend sans token :
   - `/api/library/entities` ;
   - `/api/library/platforms` ;
   - `/api/library/studios` ;
   - `/api/library/games`.
4. Vérifier les endpoints avec recherche par `name`.
5. Vérifier les endpoints avec pagination.
6. Vérifier les endpoints avec tri simple et tri multiple.
7. Vérifier les routes frontend sans utilisateur connecté.
8. Vérifier les routes frontend avec utilisateur connecté.
9. Vérifier que les pages ne proposent aucune action de modification.
10. Vérifier que les données privées utilisateur ne sont jamais visibles.
11. Rebuilder les images Docker si le comportement runtime est modifié.

## Critères d'acceptation

- Les tests backend passent.
- Le build frontend passe.
- Les pages Bibliothèque sont accessibles publiquement.
- Les listes sont consultables, paginées, recherchables et triables.
- Le menu principal affiche Bibliothèque pour tous les visiteurs.
- Aucune donnée de collection privée n'est exposée.

## Validation attendue

- `./test_backend.sh`
- `npm run build`
- Build Docker backend/frontend si nécessaire.
