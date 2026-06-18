# 00 - Analyse du code existant et contrat cible

## Objectif

Analyser l'existant avant toute modification applicative et confirmer le contrat
technique de la fonctionnalité d'images de plateformes.

Cette tâche ne doit pas modifier le code applicatif. Elle doit produire le
rapport utilisé par les sous-tâches suivantes.

## Documentation À Lire

- `tasks/0.2.6/add_image_to_plateforme/add_image.md`
- `documentation/backend-api.md`
- `documentation/authentication.md`
- `documentation/backend-arch.md`
- `documentation/frontend-arch.md`
- `documentation/database.md`
- `documentation/site-plan.md`
- `documentation/menu.md`

## Analyse Backend

Identifier et documenter :

- les routes actuelles de consultation des plateformes Bibliothèque ;
- les contrôleurs, services et repositories impliqués dans `t_platform` ;
- les modèles ORM et migrations Alembic existants ;
- les patterns existants de pagination ;
- les patterns existants de configuration par variable d'environnement ;
- les services d'envoi d'email et de notification administrateur ;
- les mécanismes d'authentification `USER` et `ADMIN` ;
- les tests backend à créer ou modifier.

## Analyse Frontend

Identifier et documenter :

- la page de détail public d'une plateforme ;
- le service `LibraryApi` et les hooks de détail plateforme ;
- la page Configuration et les actions réservées aux profils `ADMIN` ;
- les composants de tableau paginé réutilisables ;
- les styles et composants existants pour boutons, messages, miniatures et
  modales.

## Contrat Cible À Confirmer

Le rapport doit préciser les noms exacts des fichiers, classes, méthodes,
fonctions et tests à créer ou modifier pour :

- la table `t_platform_image` ;
- les enums `MAIN`, `OTHER`, `WAITING_VALIDATION`, `ACCEPTED` ;
- la contrainte unique garantissant une seule image `MAIN` par plateforme ;
- la configuration `BACKEND_IMG_DIR` et `PLATFORM_IMAGE_MAX_UPLOAD_BYTES` ;
- le stockage disque dans `/images/platforms/{slug nom}` ;
- le champ multipart `image` ;
- les extensions et MIME acceptés ;
- les endpoints publics et protégés ;
- le format JSON retourné par `GET /api/library/platforms/{id}` ;
- les règles de cache-busting ;
- les règles d'accès frontend selon le profil connecté.

## Livrable

Créer le fichier :

```text
tasks/0.2.6/add_image_to_plateforme/00_existing_code_analysis_result.md
```

Le rapport doit contenir :

- une cartographie du code existant ;
- l'architecture cible proposée ;
- les décisions de contrat utiles aux sous-tâches suivantes ;
- les risques et conflits éventuels avec `documentation/*.md` ;
- les tests et validations à exécuter.

## Critères D'Acceptation

- Le rapport existe.
- Aucun code applicatif n'est modifié.
- Les sous-tâches suivantes peuvent être réalisées sans nouvelle analyse
  générale.
