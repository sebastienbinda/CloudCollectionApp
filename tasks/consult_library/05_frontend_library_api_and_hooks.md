# 05 - API frontend et hooks Bibliothèque

## Objectif

Ajouter la couche frontend qui consomme les endpoints Bibliothèque sans mélanger ce domaine avec les workflows de collection privée.

## Étapes

1. Créer ou étendre un service frontend dédié aux endpoints `/api/library`.
2. Ajouter les fonctions d'appel pour :
   - `GET /api/library/entities` ;
   - `GET /api/library/platforms` ;
   - `GET /api/library/studios` ;
   - `GET /api/library/games`.
3. Réutiliser le garde-fou de disponibilité backend existant.
4. Créer les hooks de domaine nécessaires pour charger :
   - les compteurs de la page Bibliothèque ;
   - la liste des plateformes ;
   - la liste des studios ;
   - la liste des jeux.
5. Gérer les états de chargement, erreur, recherche, pagination et tri.

## Critères d'acceptation

- Le frontend ne contient pas de logique métier de comptage.
- Les appels backend sont isolés dans un service dédié.
- Les hooks restent organisés par domaine.
- Les erreurs réseau respectent le garde-fou déjà documenté.

## Validation attendue

- Lancer `npm run build`.
- Vérifier si `documentation/frontend-arch.md` doit être mise à jour.
