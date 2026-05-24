# 06 - Composants frontend reutilisables

## Objectif

Centraliser les composants de cartes et de tableaux avant de construire les
pages Bibliotheque.

## Etapes

1. Normaliser le rendu des cartes de la page accueil en composants
   reutilisables :
   - `GridComponent` pour remplacer l'usage direct de `platformGrid` ;
   - `CardComponent` pour remplacer l'usage direct de `platformCard` ;
   - `CardHeaderComponent` pour remplacer l'usage direct de
     `platformCardHeader` ;
   - `CardCountComponent` pour remplacer l'usage direct de
     `platformGameCount`.
2. Migrer la page accueil vers ces composants sans regression visuelle.
3. Centraliser `GameTable` en composant reutilisable `TableComponent`.
4. Utiliser `TableComponent` pour les tableaux collection et wishlist existants.
5. Centraliser la gestion UI de pagination dans `TableComponent` :
   - affichage de la page courante ;
   - navigation page precedente / page suivante ;
   - choix de taille de page si expose ;
   - desactivation des controles non disponibles ;
   - callbacks vers le hook appelant pour charger une autre page.
6. Conserver les capacites existantes du tableau :
   - colonnes ;
   - libelles ;
   - tri ;
   - filtres ;
   - classes responsives ;
   - actions de ligne optionnelles.

## Criteres d'acceptation

- La page accueil utilise `GridComponent`, `CardComponent`,
  `CardHeaderComponent` et `CardCountComponent`.
- Les tableaux existants ne dependent plus directement de `GameTable` comme
  composant specifique aux jeux.
- Le point d'entree reutilisable des tableaux est `TableComponent`.
- La pagination visible et ses controles sont portes par `TableComponent`, pas
  reimplementes dans chaque page.
- Les workflows collection et wishlist existants restent fonctionnels.

## Validation attendue

- Lancer `npm run build`.
- Tester manuellement accueil, detail plateforme et wishlist.
- Verifier le responsive des cartes et tableaux.
