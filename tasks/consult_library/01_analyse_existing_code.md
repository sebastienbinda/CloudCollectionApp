# 01 - Analyse du code existant

## Objectif

Identifier les modèles, repositories, routes, composants et styles existants à réutiliser pour créer la Bibliothèque publique.

## Étapes

1. Lire `tasks/consult_library/consult.md`.
2. Identifier les modèles backend représentant les plateformes, studios et jeux.
3. Identifier les repositories ou services existants permettant de lire ces entités.
4. Identifier les routes publiques existantes et les conventions de contrôleur Flask.
5. Identifier les composants frontend existants utilisés pour :
   - les cartes de plateforme de la page accueil ;
   - les tableaux de collection ;
   - les tableaux de wishlist ;
   - le menu principal.
6. Vérifier les règles applicables dans `documentation/backend-arch.md`, `documentation/frontend-arch.md`, `documentation/backend-api.md`, `documentation/site-plan.md` et `documentation/menu.md`.
7. Produire un court rapport d'analyse dans `tasks/consult_library/01_existing_code_analysis_result.md`.

## Critères d'acceptation

- Le rapport liste les fichiers backend à réutiliser ou étendre.
- Le rapport liste les fichiers frontend à réutiliser ou étendre.
- Le rapport indique clairement si de nouveaux repositories, services, hooks ou composants sont nécessaires.
- Le rapport confirme que les routes Bibliothèque doivent rester publiques et en lecture seule.

## Validation attendue

- Aucune modification fonctionnelle n'est réalisée pendant cette tâche.
- Les documentations liées sont lues avant les tâches de développement.
