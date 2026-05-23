# 03 - Service de lecture ODS

## Objectif

Centraliser la lecture des fichiers ODS dans un service dédié et factoriser le code existant.

## Étapes

1. Créer ou adapter un service backend dédié à la lecture des fichiers de collection ODS.
2. Réutiliser le code existant de lecture ODS au lieu de dupliquer la logique.
3. Ignorer les onglets non importés :
   - `Accueil`
   - `Liste de souhaits`
4. Considérer les autres onglets comme des onglets de plateforme importables.
5. Valider la présence des colonnes attendues dans chaque onglet plateforme importable.
6. Retourner une structure métier claire contenant :
   - plateformes
   - studios
   - jeux
7. Gérer les dates de sortie vides ou invalides avec une valeur `NULL` et un warning dans les logs.
8. Préparer le service pour permettre plus tard d'autres formats de fichier.
9. Vider le cache ODS associé au fichier d'import en fin de lecture, en succès comme en erreur.

## Critères d'acceptation

- Toute la lecture ODS passe par un service unique.
- Le service ne fait pas d'écriture en base.
- Le service ne dépend pas d'un contrôleur HTTP.
- Un fichier sans onglet plateforme importable est rejeté.
- Un onglet plateforme importable sans colonnes attendues est rejeté.
- Le cache ODS du fichier d'import est libéré après le traitement pour éviter de conserver en mémoire des données d'import ponctuelles.

## Validation attendue

- Ajouter ou mettre à jour les tests unitaires du lecteur ODS.
- Tester les cas :
   - fichier valide
   - fichier illisible
   - fichier sans onglet plateforme importable
   - onglet avec colonnes manquantes
   - date vide
   - date invalide
   - vidage du cache après lecture
