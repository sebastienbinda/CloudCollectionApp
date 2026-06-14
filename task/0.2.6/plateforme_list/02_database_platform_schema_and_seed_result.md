# 02 - Résultat schéma SQL plateformes et chargement initial

## Résumé

La tâche 2 a été implémentée côté backend.

## Changements Réalisés

- Ajout d'une migration Alembic `20260614_0008_platform_catalog_schema.py`.
- Ajout de `t_platform.end_date`.
- Suppression de `t_platform.status`.
- Conservation de `release_date`, `manufacturer` et `description` en colonnes
  nullables.
- Ajout d'un service de lecture et seed CSV :
  `PlatformCatalogCsvReader` et `PlatformCatalogSeedService`.
- Découpage conforme a la règle `un fichier par classe` pour les nouveaux
  fichiers applicatifs et les helpers/tests ajoutés sur cette tâche.
- Chargement initial depuis :
  `backend/services/database/platform_catalog.csv`, copie runtime du contrat
  `task/0.2.6/plateforme_list/consoles_jeux_video.csv`.
- Seed idempotent par clé fonctionnelle trimmee, minuscule et sans accents.
- Conservation de la ponctuation significative dans la clé, notamment `+` pour
  distinguer `Atari 7800` et `Atari 7800+`.
- Adaptation du repository plateformes public et du payload bibliothèque :
  `release_date`, `end_date`, `manufacturer`, `description`, `total_games`.
- Autorisation du tri public des plateformes par `end_date`.
- Ajout d'un cache serveur `PlatformCatalogCache` pour le catalogue plateformes,
  avec expiration toutes les 5 heures.
- Le repository plateformes utilise ce cache pour les imports et la recherche
  publique ; les insertions plateforme invalident le cache par prudence.

## Règles CSV Appliquées

- `YYYY-MM-DD` reste une date exacte.
- `YYYY-MM` devient le premier jour du mois.
- `YYYY` devient le 1er janvier.
- `Inconnue` devient `NULL`.
- `En vente` devient `NULL` uniquement pour `date_retrait_vente`.
- `En vente` est rejeté pour `date_mise_en_vente`.

## Tests Ajoutés Ou Modifiés

- Tests du lecteur CSV plateformes.
- Tests du seed idempotent.
- Tests de distinction `Atari 7800` / `Atari 7800+`.
- Tests de déclaration de migration.
- Tests du repository plateformes public.
- Tests du payload bibliothèque plateformes.
- Test de tri `end_date` dans le parser bibliothèque.

## Validations

- Tests ciblés backend :
  `36 tests`, statut `OK`.
- Suite backend complète :
  `371 tests`, statut `OK`.
- Reconstruction Docker :
  `docker compose -f docker/docker-compose.yml build`, statut `OK`.

## Points Pour Les Tâches Suivantes

- Les vues frontend plateformes affichent encore l'ancienne colonne `status`.
  Elles doivent être adaptées dans la tâche frontend dédiée.
- `documentation/database.md` et `documentation/backend-api.md` devront être mis
  à jour dans la tâche documentation finale pour refléter `end_date` et
  l'absence de `status` côté plateformes publiques.
- `documentation/backend-arch.md` devra aussi documenter que le cache plateformes
  est un cache serveur partagé par l'import et la recherche, avec TTL 5h.
