# 01 - Contrat de configuration wishlist

## Objectif

Stabiliser le contrat JSON de configuration wishlist, les règles fonctionnelles
et les validations backend avant de modifier le parsing réel du fichier.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.0/import_wishlist/00_existing_code_analysis_result.md`
- `tasks/0.2.0/import_wishlist/import_wishlist.md`

## Contrat Wishlist

Confirmer et implémenter le contrat final proposé dans le rapport d'analyse pour
les trois modes :

- `wishlist.mode = "none"` : aucune information wishlist dans le fichier ;
- `wishlist.mode = "sheet"` : un onglet dédié contient les souhaits ;
- `wishlist.mode = "column"` : une colonne de chaque onglet de collection porte
  l'information.

## Validations Attendues

Ajouter les validations backend nécessaires pour refuser une configuration
wishlist incohérente avec un `422` explicite :

- `wishlist` absent ;
- `wishlist.mode` absent ;
- `wishlist.mode` inconnu ;
- mode `sheet` sans `sheet_name` ;
- mode `sheet` sans `data_range`, `header_row` ou `column_information`
  obligatoire ;
- mode `sheet` avec une colonne `wishlist` inutile dans `column_information` ;
- mode `column` sans mapping `wishlist` dans les configurations de collection ;
- mode `none` avec une configuration de sheet ou de colonne ;
- toute incohérence supplémentaire identifiée dans
  `00_existing_code_analysis_result.md`.

## Règles Fonctionnelles À Formaliser

Formaliser dans le code les règles confirmées par le rapport :

- valeurs booléennes acceptées : `Oui/Non`, `O/N`, `True/False`, `Yes/No`,
  `Y/N`, sans tenir compte de la casse ;
- valeur vide en mode `column` : `wishlist=false` ;
- valeur invalide en mode `column` : ligne ignorée, warning de log et compteur
  de warning dans le retour ;
- mode `sheet` : toutes les lignes valides de l'onglet dédié sont importées avec
  `wishlist=true` ;
- priorité finale en cas de doublon collection/wishlist selon la règle décidée
  dans le rapport d'analyse.

## Tests Attendus

Ajouter ou modifier des tests backend couvrant :

- chaque mode wishlist valide ;
- chaque validation `422` listée ci-dessus ;
- parsing des valeurs booléennes acceptées ;
- valeur vide ;
- valeur invalide ;
- priorité des doublons.

## Critères D'Acceptation

- Le contrat wishlist est représenté par des objets ou DTOs dédiés.
- Le controller ne contient pas de logique de validation métier.
- Les validations retournent un statut et un payload cohérents avec les
  validations d'import existantes.
- Les tests backend ciblés passent.
