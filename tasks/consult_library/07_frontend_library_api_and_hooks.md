# 07 - API frontend et hooks Bibliotheque

## Objectif

Ajouter la couche frontend qui consomme les endpoints Bibliotheque sans melanger
ce domaine avec les workflows de collection privee.

## Etapes

1. Creer ou etendre un service frontend dedie aux endpoints `/api/library`.
2. Ajouter les fonctions d'appel pour :
   - `GET /api/library/entities` ;
   - `GET /api/library/platforms` ;
   - `GET /api/library/studios` ;
   - `GET /api/library/games`.
3. Reutiliser le garde-fou de disponibilite backend existant.
4. Creer les hooks de domaine necessaires pour charger :
   - les compteurs de la page Bibliotheque ;
   - la liste des plateformes ;
   - la liste des studios ;
   - la liste des jeux.
5. Gerer les etats de chargement, erreur, recherche, pagination et tri.
6. Fournir a `TableComponent` les metadonnees et callbacks de pagination sans
   rendre les controles de pagination directement dans les pages.

## Criteres d'acceptation

- Le frontend ne contient pas de logique metier de comptage.
- Les appels backend sont isoles dans un service dedie.
- Les hooks restent organises par domaine.
- Les erreurs reseau respectent le garde-fou deja documente.
- La logique d'etat reste dans les hooks, mais le rendu et l'orchestration UI
  de pagination sont centralises dans `TableComponent`.

## Validation attendue

- Lancer `npm run build`.
- Verifier si `documentation/frontend-arch.md` doit etre mise a jour.
