<!--
    ____ _                 _  ____      _ _           _   _             ___
   / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
  | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
  | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
   \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
                                                                             |_|   |_|
  Projet : CloudCollectionApp
  Date de creation : 2026-05-03
  Auteurs : Codex et Binda Sébastien
-->
# Schema de base de donnees

## Conventions

- Base cible : PostgreSQL
- Les noms de tables, colonnes, sequences et contraintes sont en `snake_case`.
- Les identifiants techniques sont de type `BIGINT`.
- Les champs JSON utilisent le type PostgreSQL `JSONB`.
- Les dates utilisent le type `TIMESTAMP`.

## Tables

### t_schema_version

| Colonne | Type | Null | Description |
| --- | --- | --- | --- |
| `version` | `VARCHAR(5)` | Non | Version applicative inscrite apres initialisation du schema. |
| `date_creation` | `TIMESTAMP` | Non | Date de premiere creation du schema. |
| `update_date` | `TIMESTAMP` | Oui | Date de derniere mise a jour de la version applicative. |

Contraintes :

- Cle primaire : `version`

### t_platform

| Colonne | Type | Null | Description |
| --- | --- | --- | --- |
| `id` | `BIGINT` | Non | Identifiant technique genere par `s_platform`. |
| `name` | `VARCHAR(64)` | Non | Nom de la plateforme. |
| `release_date` | `TIMESTAMP` | Oui | Date de sortie de la plateforme. |
| `manufacturer` | `VARCHAR(128)` | Oui | Fabricant de la plateforme. |
| `description` | `JSONB` | Oui | Description structuree de la plateforme. |
| `status` | `VARCHAR(16)` | Non | Statut fonctionnel de la plateforme. |

Contraintes :

- Cle primaire : `id`

### t_studio

| Colonne | Type | Null | Description |
| --- | --- | --- | --- |
| `id` | `BIGINT` | Non | Identifiant technique genere par `s_studio`. |
| `name` | `VARCHAR(256)` | Non | Nom du studio. |
| `country` | `VARCHAR(256)` | Oui | Pays du studio. |
| `city` | `VARCHAR(256)` | Oui | Ville du studio. |
| `creation_date` | `TIMESTAMP` | Oui | Date de creation du studio. |
| `status` | `VARCHAR(16)` | Non | Statut fonctionnel du studio. |

Contraintes :

- Cle primaire : `id`
- Cle unique : `name`

### t_game

| Colonne | Type | Null | Description |
| --- | --- | --- | --- |
| `id` | `BIGINT` | Non | Identifiant technique genere par `s_game`. |
| `name` | `VARCHAR(256)` | Non | Nom du jeu. |
| `release_date` | `TIMESTAMP` | Oui | Date de sortie du jeu. |
| `developper` | `BIGINT` | Oui | Studio de developpement du jeu. |
| `editor` | `BIGINT` | Oui | Studio editeur du jeu. |
| `platform` | `BIGINT` | Non | Plateforme du jeu. |
| `description` | `JSONB` | Oui | Description structuree du jeu. |

Contraintes :

- Cle primaire : `id`
- Cle unique : `name`, `platform`
- Cle etrangere : `developper` -> `t_studio.id`
- Cle etrangere : `editor` -> `t_studio.id`
- Cle etrangere : `platform` -> `t_platform.id`

### t_user

| Colonne | Type | Null | Description |
| --- | --- | --- | --- |
| `id` | `BIGINT` | Non | Identifiant technique genere par `s_user`. |
| `email` | `VARCHAR(256)` | Non | Adresse email de l'utilisateur. |
| `password_encrypted` | `VARCHAR(512)` | Non | Mot de passe chiffre. |
| `creation_date` | `TIMESTAMP` | Non | Date de creation de l'utilisateur. |
| `last_connexion_date` | `TIMESTAMP` | Oui | Date de derniere connexion. |
| `collection_file_path` | `VARCHAR(512)` | Oui | Chemin du fichier de collection rattache. |
| `collection_file_description` | `JSONB` | Oui | Description structuree du fichier de collection. |

Contraintes :

- Cle primaire : `id`
- Cle unique : `email`

### t_user_collection

| Colonne | Type | Null | Description |
| --- | --- | --- | --- |
| `user_id` | `BIGINT` | Non | Utilisateur proprietaire de l'entree de collection. |
| `game_id` | `BIGINT` | Non | Jeu rattache a l'utilisateur. |
| `game_additional_name` | `VARCHAR(256)` | Oui | Nom complementaire du jeu dans la collection utilisateur. |

Contraintes :

- Cle primaire : `user_id`, `game_id`
- Cle etrangere : `user_id` -> `t_user.id`
- Cle etrangere : `game_id` -> `t_game.id`

## Sequences

| Sequence | Table | Colonne |
| --- | --- | --- |
| `s_platform` | `t_platform` | `id` |
| `s_studio` | `t_studio` | `id` |
| `s_game` | `t_game` | `id` |
| `s_user` | `t_user` | `id` |
