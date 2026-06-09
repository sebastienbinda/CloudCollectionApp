# 02 - Composants collection partagés

## Objectif

Factoriser le rendu React commun entre la page plateforme et la future page
wishlist, sans changer le comportement fonctionnel de la page plateforme.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.0/user_wishlist_view/00_existing_code_analysis_result.md`
- `tasks/0.2.0/user_wishlist_view/user_wishlist_view.md`

## Périmètre

Centraliser uniquement le rendu partagé de consultation des jeux :

- tableau ;
- filtres de colonnes ;
- tri ;
- états de chargement ;
- états vide et erreur ;
- éventuel calcul de classe de ligne déjà utilisé.

## Règles Attendues

- La page plateforme doit continuer à afficher son sélecteur de plateforme.
- La page plateforme doit conserver ses actions existantes si elles sont déjà
  présentes.
- La page wishlist doit pouvoir désactiver le sélecteur de plateforme.
- La page wishlist doit pouvoir désactiver toutes les actions de ligne.
- Le composant partagé doit être piloté par une configuration explicite plutôt
  que par des conditions implicites dispersées.
- Le composant partagé ne doit pas faire d'appel HTTP.
- Les appels HTTP restent dans les services frontend.
- L'orchestration d'état reste dans les hooks.
- Le rendu reste dans les composants React.
- Aucun nouveau framework ou dépendance ne doit être ajouté.

## Critères D'Acceptation

- La page plateforme utilise le composant ou la configuration partagée.
- Le comportement visible de la page plateforme reste inchangé.
- Le composant partagé permet de configurer :
  - les colonnes visibles ;
  - les colonnes filtrables ;
  - les colonnes triables ;
  - le tri par défaut ;
  - l'affichage ou non des actions ;
  - l'affichage ou non du sélecteur de plateforme.
- Les fichiers créés ou modifiés respectent les limites de taille du projet.

## Validation Attendue

- Lancer `npm run build` depuis `frontend/`.
- Vérifier manuellement, si un serveur local est disponible :
  - chargement d'une page plateforme ;
  - tri de la table plateforme ;
  - filtres existants de la page plateforme ;
  - actions existantes de la page plateforme.
