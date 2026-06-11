# Analyse existante et contrat

## Objectif

Identifier les composants existants à réutiliser pour le reset Bibliotheque et
figer le contrat technique avant toute modification de code.

## Périmètre

- Lire `documentation/backend-arch.md`, `documentation/backend-api.md`,
  `documentation/bibliotheque.md`, `documentation/import.md`,
  `documentation/site-plan.md` et `documentation/database.md`.
- Rechercher les contrôleurs, services, repositories et tests existants autour
  de la Bibliotheque, de l'import utilisateur, de la réinitialisation de
  collection et de l'envoi d'email.
- Identifier le service d'import existant qui doit être réutilisé pour chaque
  utilisateur.
- Identifier les routes d'import à bloquer pendant un reset.
- Vérifier les contraintes de clés étrangères entre `t_user_collection`,
  `t_game`, `t_platform` et `t_studio`.
- Confirmer le conflit documentaire assumé : la Bibliotheque reste publique en
  consultation, mais un endpoint protégé `ADMIN` permet le reset.

## Livrable attendu

Créer un rapport `00_existing_code_analysis_result.md` dans ce dossier avec :

- les fichiers existants à modifier ;
- les patterns à réutiliser ;
- le contrat final de `POST /api/library/reset` ;
- la liste exacte des endpoints d'import bloqués pendant reset ;
- les tests à créer ou modifier ;
- les points de documentation impactés.

## Critères d'acceptation

- Aucun code applicatif n'est modifié dans cette sous-tâche.
- Le rapport permet de commencer les sous-tâches suivantes sans nouvelle
  recherche d'architecture majeure.
