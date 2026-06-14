# 04 - Contrat du résultat d'import

## Objectif

Remplacer la notion de plateformes créées pendant l'import par la notion de
plateformes liées à l'import.

Cette tâche doit s'appuyer sur :

- `task/0.2.6/plateforme_list/00_existing_code_analysis_result.md`
- `task/0.2.6/plateforme_list/03_backend_platform_matching_import.md`
- `documentation/backend-api.md`
- `documentation/import.md`

## Backend À Modifier

Selon les noms confirmés dans le rapport d'analyse :

- DTO / dataclass de résultat de persistance ;
- service d'import ;
- controller d'import ;
- tests de route et de service.

## Règles Fonctionnelles

- Le résultat d'import ne doit plus présenter `created_platforms` comme un
  enrichissement du référentiel commun.
- Le résultat doit exposer le nombre de plateformes du référentiel liées aux
  jeux importés.
- Le contrat doit rester clair pour les imports partiels ou avec warnings.
- Les anciens champs ne doivent être conservés que si le rapport d'analyse
  justifie une période de compatibilité.

## Tests Attendus

Ajouter ou modifier des tests backend couvrant :

- import avec une seule plateforme liée ;
- import avec plusieurs plateformes liées ;
- import avec plateformes en doublon dans le fichier utilisateur ;
- import avec plateformes incertaines et warnings ;
- sérialisation du nouveau compteur dans la réponse HTTP.

## Critères D'Acceptation

- Le backend retourne le nouveau compteur.
- Les tests backend du contrat d'import passent.
- Le frontend peut consommer le résultat sans ambiguïté.
