# 08 - Documentation finale

## Objectif

Mettre à jour la documentation fonctionnelle et technique après validation de
la fonctionnalité.

Cette tâche dépend de `07_validation_and_docker.md`.

## Documentation À Mettre À Jour

Mettre à jour au minimum :

- `documentation/bibliotheque.md` ;
- `documentation/backend-api.md` ;
- `documentation/database.md` ;
- `documentation/site-plan.md` ;
- `documentation/authentication.md`.

Vérifier aussi si des mises à jour sont nécessaires dans :

- `documentation/backend-arch.md` ;
- `documentation/frontend-arch.md` ;
- `documentation/menu.md` ;
- `README.md`.

## Contenu Attendu

Documenter :

- le champ `t_game.status` et ses contraintes ;
- les statuts `WAITING_VALIDATION` et `ACCEPTED` ;
- les règles de création selon import utilisateur, import admin CSV et reset ;
- les règles de visibilité Bibliothèque par profil ;
- le comportement de `GET /api/library/games` et
  `GET /api/library/games/<game_id>` ;
- les endpoints admin de validation/refus ;
- le résumé admin et le compteur de jeux en attente ;
- la notification quotidienne admin ;
- les emails utilisateurs après refus ;
- les règles frontend du filtre statut, badge menu et message de reset ;
- les commandes de validation ou changements README si nécessaires.

## Contraintes

- Ne pas affaiblir les règles de sécurité existantes.
- Conserver la Bibliothèque publique read-only pour les endpoints publics.
- Documenter clairement les exceptions protégées `ADMIN`.
- Respecter la gouvernance documentaire du projet et attendre confirmation si
  une règle existante doit être remplacée ou affaiblie.

## Critères D'Acceptation

- Les documentations concernées décrivent le comportement livré.
- Le README est mis à jour ou explicitement déclaré non concerné.
- Le rapport final contient une ligne de conformité par documentation concernée,
  avec les marqueurs demandés par `AGENTS.md`.
