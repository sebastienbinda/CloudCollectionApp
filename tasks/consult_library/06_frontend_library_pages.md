# 06 - Pages frontend Bibliothèque

## Objectif

Créer les pages publiques de consultation Bibliothèque et les intégrer au menu principal.

## Étapes

1. Ajouter la route `/bibliotheque`.
2. Ajouter la route `/bibliotheque/plateformes`.
3. Ajouter la route `/bibliotheque/studios`.
4. Ajouter la route `/bibliotheque/jeux`.
5. Ajouter l'entrée Bibliothèque dans le menu principal pour tous les visiteurs.
6. Créer la page Bibliothèque avec trois cartes :
   - Plateformes ;
   - Studios ;
   - Jeux.
7. Réutiliser le rendu des cartes de la page accueil autant que possible.
8. Créer les pages de listes en réutilisant le rendu des tableaux de collection et wishlist.
9. Ajouter un champ de recherche par nom au-dessus de chaque tableau.
10. Ajouter la pagination et le tri des colonnes autorisées.
11. Vérifier que les pages restent consultables sans authentification.

## Critères d'acceptation

- Les quatre routes frontend sont accessibles sans connexion.
- La page Bibliothèque affiche les compteurs globaux.
- Les pages d'entités affichent les données paginées.
- La recherche par nom fonctionne sur chaque page d'entité.
- Les pages sont en lecture seule : aucun bouton d'ajout, édition ou suppression.
- Le rendu reste cohérent avec les composants existants.

## Validation attendue

- Lancer `npm run build`.
- Tester manuellement les routes avec et sans utilisateur connecté.
- Vérifier le responsive si la page ajoute de nouveaux styles.
