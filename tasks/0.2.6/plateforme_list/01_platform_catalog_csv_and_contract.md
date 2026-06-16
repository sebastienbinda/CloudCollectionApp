# 01 - Contrat du catalogue plateformes et CSV

## Objectif

Stabiliser le contrat de données du référentiel plateformes fourni par
l'application avant de modifier la base de données.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.6/plateforme_list/00_existing_code_analysis_result.md`
- `tasks/0.2.6/plateforme_list/consoles_jeux_video.csv`
- `tasks/0.2.6/plateforme_list/plateforme_list.md`

## Travail À Réaliser

- Valider que le CSV est lisible avec les colonnes :
  - `nom_machine`
  - `nom_fabricant`
  - `date_mise_en_vente`
  - `date_retrait_vente`
- Définir le mapping CSV vers `t_platform` :
  - `nom_machine` vers `name` ;
  - `nom_fabricant` vers `manufacturer` ;
  - `date_mise_en_vente` vers `release_date` ;
  - `date_retrait_vente` vers `end_date` ;
  - `description` avec une structure vide ou enrichie selon le rapport
    d'analyse.
- Définir la règle de conversion des dates partielles (`YYYY`, `YYYY-MM`) et
  des valeurs `Inconnue` / `En vente`.
- Corriger le CSV uniquement si l'analyse identifie des erreurs bloquantes de
  format.

## Tests / Validations Attendus

- Ajouter ou préparer un test backend de parsing du CSV si une classe dédiée est
  créée.
- Vérifier qu'aucune ligne CSV n'a un nombre de colonnes invalide.
- Vérifier qu'aucun nom de plateforme vide n'est accepté.

## Critères D'Acceptation

- Le contrat CSV vers base est documenté dans le code ou le rapport
  d'implémentation.
- Les valeurs inconnues ne sont pas converties en fausses dates.
- Les règles de conversion peuvent être réutilisées par la migration ou le
  seed applicatif.
