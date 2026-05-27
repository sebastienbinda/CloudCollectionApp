# 08 - Pages frontend Bibliotheque

## Objectif

Creer les pages publiques de consultation Bibliotheque et les integrer au menu
principal.

## Etapes

1. Ajouter la route `/bibliotheque`.
2. Ajouter la route `/bibliotheque/plateformes`.
3. Ajouter la route `/bibliotheque/studios`.
4. Ajouter la route `/bibliotheque/jeux`.
5. Ajouter l'entree Bibliotheque dans le menu principal pour tous les visiteurs.
6. Creer la page Bibliotheque avec trois cartes :
   - Plateformes ;
   - Studios ;
   - Jeux.
7. Reutiliser les composants de cartes crees dans la tache 06.
8. Creer les pages de listes avec `TableComponent`.
9. Ajouter un champ de recherche par nom au-dessus de chaque tableau.
10. Ajouter le tri des colonnes autorisees.
11. Verifier que les pages restent consultables sans authentification.

## Criteres d'acceptation

- Les quatre routes frontend sont accessibles sans connexion.
- La page Bibliotheque affiche les compteurs globaux.
- Les pages d'entites affichent les donnees paginees.
- La recherche par nom fonctionne sur chaque page d'entite.
- Les pages sont en lecture seule : aucun bouton d'ajout, edition ou
  suppression.
- Les cartes de la page Bibliotheque utilisent `GridComponent`,
  `CardComponent`, `CardHeaderComponent` et `CardCountComponent`.
- Les listes utilisent `TableComponent`.

## Validation attendue

- Lancer `npm run build`.
- Tester manuellement les routes avec et sans utilisateur connecte.
- Verifier le responsive si la page ajoute de nouveaux styles.
