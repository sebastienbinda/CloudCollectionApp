# 04 - Normalisation et déduplication

## Objectif

Ajouter la normalisation métier utilisée pour comparer les plateformes, studios et jeux sans créer de doublons.

## Étapes

1. Créer ou réutiliser un utilitaire de normalisation.
2. Implémenter la valeur stockée :
   - `trim()`
   - casse et accents conservés
3. Implémenter la clé de comparaison :
   - `trim().lower()`
   - accents supprimés par normalisation Unicode
4. Utiliser cette normalisation pour :
   - plateformes
   - studios
   - jeux
5. Dédupliquer les doublons présents dans le fichier ODS.
6. Conserver uniquement la première occurrence.
7. Ajouter un warning dans les logs pour les doublons ignorés.

## Critères d'acceptation

- Deux valeurs qui ne diffèrent que par les accents sont considérées équivalentes.
- Deux valeurs qui ne diffèrent que par les espaces externes ou la casse sont considérées équivalentes.
- La valeur insérée en base garde la casse et les accents de la première occurrence.
- Les doublons du fichier ne bloquent pas l'import.

## Validation attendue

- Ajouter des tests unitaires pour la normalisation.
- Ajouter des tests pour les doublons de plateformes, studios et jeux.
