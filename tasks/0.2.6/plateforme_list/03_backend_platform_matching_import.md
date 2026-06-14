# 03 - Matching des plateformes pendant l'import

## Objectif

Modifier l'import utilisateur pour ne plus créer de plateformes depuis les
fichiers utilisateurs et pour rattacher les jeux importés au référentiel
applicatif existant.

Cette tâche doit s'appuyer sur :

- `tasks/0.2.6/plateforme_list/00_existing_code_analysis_result.md`
- `documentation/import.md`
- `documentation/backend-arch.md`

## Backend À Modifier

Selon les noms confirmés dans le rapport d'analyse :

- service d'import utilisateur ;
- repository de plateformes ;
- normaliseur de noms ;
- éventuel service de fuzzy matching ;
- objet de configuration des seuils de matching ;
- modèle de warnings d'import ;
- service d'email administrateur.

## Règles Fonctionnelles

- L'import ne doit plus insérer de nouvelles plateformes dans `t_platform`.
- Le matching d'import doit utiliser le cache serveur du catalogue plateformes
  quand il charge les plateformes candidates.
- Le cache plateformes expire toutes les 5 heures ; aucun cache local plus long
  ne doit être ajouté dans le matching.
- La recherche doit ignorer les différences de casse, espaces et accents.
- Une coquille dans le nom peut être corrigée par correspondance approximative
  selon les seuils définis dans la tâche chapeau.
- Les seuils par défaut à respecter sont :
  - `100%` : match parfait, import sans warning plateforme ;
  - `75% <= score < 100%` : match suffisamment fiable, import sans warning
    plateforme sauf ambiguïté ;
  - `25% <= score < 75%` : match faible, import avec warning, vérification
    manuelle et email administrateur ;
  - `0% < score < 25%` : score trop faible, pas d'import du jeu et warning ;
  - `0%` : match inexistant, pas d'import du jeu et warning.
- Les seuils `25%` et `75%` doivent être configurables par variables
  d'environnement :
  - `MATCHING_LOW_LVL_RATING`, valeur par défaut `25` ;
  - `MATCHING_HIGH_LEVEL_RATING`, valeur par défaut `75`.
- La configuration doit être validée au démarrage du service de matching :
  - valeurs numériques entre `0` et `100` ;
  - seuil bas strictement inférieur au seuil haut ;
  - valeurs invalides refusées avec une erreur explicite.
- Si le score demande une vérification manuelle :
  - les jeux concernés doivent être listés dans les warnings de retour
    d'import ;
  - un email doit être envoyé à l'administrateur configuré en `.env` ;
- les jeux concernés peuvent être importés seulement dans la tranche
  `25% <= score < 75%`.
- Aucun secret, mot de passe ou token ne doit être codé en dur.

## Tests Attendus

Ajouter des tests backend poussés couvrant :

- correspondance exacte ;
- différence de casse ;
- différence d'accents ;
- espaces supplémentaires ;
- coquille mineure acceptée ;
- score entre 25% et 75% accepté avec warning et email ;
- score inférieur à 25% refusé ;
- score à 0% refusé comme match inexistant ;
- seuils personnalisés via variables d'environnement ;
- configuration invalide refusée ;
- égalité ou ambiguïté entre deux plateformes ;
- warnings retournés avec la liste des jeux impactés ;
- email administrateur déclenché uniquement quand nécessaire ;
- absence de création de plateforme pendant l'import.
- utilisation du cache plateformes pour charger les candidates sans requêtes SQL
  répétées.

## Critères D'Acceptation

- Les plateformes importées sont rattachées au référentiel existant.
- Les cas incertains sont visibles dans les warnings.
- L'administrateur est notifié pour vérification manuelle quand le score est
  entre 25% et 75%.
- Les tests backend de matching passent.
