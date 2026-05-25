# 05 - Endpoints backend par entite

## Objectif

Exposer les endpoints publics de consultation avec un controleur backend par
entite.

## Etapes

1. Reutiliser et etendre `backend/controllers/platform_controller.py` avec
   l'orthographe anglaise correcte `platform`.
2. Creer `backend/controllers/studio_controller.py` pour les endpoints studios.
3. Creer `backend/controllers/game_controller.py` pour les endpoints jeux.
4. Exposer `GET /api/library/entities` depuis un des controleurs d'entite
   existants, de preference `PlatformController`, uniquement comme agregat de
   compteurs.
5. Exposer `GET /api/library/platforms` depuis `PlatformController`.
6. Exposer `GET /api/library/studios` depuis `StudioController`.
7. Exposer `GET /api/library/games` depuis `GameController`.
8. Brancher les parametres `name`, `page`, `size` et `sort` sur la couche de
   service.
9. Garantir que ces routes ne necessitent pas d'authentification.
10. Garantir que les reponses JSON respectent `tasks/consult_library/consult.md`.
11. Ajouter les tests de routes backend.

## Criteres d'acceptation

- Les quatre endpoints repondent sans token.
- Les endpoints sont portes par des controleurs d'entite, pas par un controleur
  Bibliotheque transverse.
- `PlatformController` reste le controleur des plateformes et utilise partout
  `platform`, jamais `plateform`.
- Les endpoints sont strictement en lecture seule.
- Les reponses de pagination contiennent `totalElements`, `page`, `size` et
  `totalPages`.
- Les erreurs de parametres invalides retombent sur les valeurs par defaut
  prevues.
- Aucun champ prive ou utilisateur n'est expose.

## Validation attendue

- Lancer les tests backend des routes.
- Lancer `./test_backend.sh`.
- Mettre a jour `documentation/backend-api.md` dans la tache documentation.
