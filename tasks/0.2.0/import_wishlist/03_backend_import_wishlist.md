# 03 - Import backend wishlist

## Objectif

Modifier le workflow backend `POST /api/users/import` pour lire, transporter et
persister l'information wishlist selon le contrat validé.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.0/import_wishlist/00_existing_code_analysis_result.md`
- `tasks/0.2.0/import_wishlist/import_wishlist.md`

## Périmètre

Implémenter dans les classes et fichiers désignés par le rapport :

- lecture du mode `wishlist.mode` ;
- extraction wishlist depuis un onglet dédié ;
- extraction wishlist depuis une colonne dédiée ;
- parsing des valeurs booléennes ;
- exclusion des lignes avec valeur wishlist invalide ;
- agrégation des warnings ;
- application des règles de doublon ;
- persistance de `wishlist` dans `t_user_collection` ;
- enrichissement du retour `POST /api/users/import`.

## Retour D'Import

Le retour doit inclure les nouveaux champs confirmés par le rapport d'analyse,
dont :

```json
{
  "created_platforms": 3,
  "created_studios": 12,
  "created_games": 42,
  "associated_games": 58,
  "wishlisted_games": 12,
  "warnings": {
    "invalid_wishlist": 3,
    "invalid_wishlist_values_found": ["Ok", "Peut etre", "Nop"]
  }
}
```

## Règles D'Architecture

- Garder la généricité du reader par type de fichier.
- Ne pas introduire de logique ODS dans le controller.
- Garder l'import transactionnel.
- Conserver la responsabilité de validation et persistance côté backend.
- Ne pas hardcoder de secrets ni de chemins utilisateur absolus.

## Tests Attendus

Ajouter ou modifier des tests backend couvrant :

- import sans wishlist ;
- import avec onglet dédié ;
- import avec colonne dédiée en `single_sheet_conf` ;
- import avec colonne dédiée en `multiple_sheets_conf.shared_layout` ;
- import avec colonne dédiée en `multiple_sheets_conf.sheets` ;
- valeurs booléennes acceptées ;
- valeurs vides ;
- valeurs invalides avec ligne ignorée et warning ;
- doublons selon les règles confirmées ;
- compteurs `wishlisted_games` et `warnings`.

## Critères D'Acceptation

- `POST /api/users/import/analyze/<file_type>` reste non impacté.
- `POST /api/users/import/file/<file_type>` reste non impacté.
- `POST /api/users/import` persiste correctement la wishlist.
- Le retour d'import contient les nouveaux compteurs.
- Les tests backend ciblés passent.
