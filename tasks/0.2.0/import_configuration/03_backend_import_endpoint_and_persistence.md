# 03 - Endpoint d'import et persistance de la configuration

## Objectif

Brancher le contrat configurable sur `POST /api/users/import`, préserver le
workflow transactionnel et sauvegarder la configuration dans
`t_user.collection_file_description` uniquement après succès.

Cette tâche dépend de :

- `01_import_configuration_contract.md`
- `02_backend_generic_reader_architecture.md`

## Endpoint

`POST /api/users/import` reçoit :

- `collection_file` : fichier uploadé ;
- `collection_file_description` : JSON de configuration validé.

Le champ `collection_file_description` est obligatoire.

## Codes Retour

Conserver les codes existants :

- `400` pour fichier invalide ou illisible ;
- `409` si la collection existe déjà ;
- `413` si le fichier dépasse la taille maximale ;
- `500` pour erreur inattendue.

Ajouter :

- `422` pour configuration invalide.

## Persistance

Si l'import réussit :

- les données SQL sont persistées transactionnellement ;
- `t_user.collection_file_path` est renseigné ;
- `t_user.collection_file_description` reçoit le JSON validé ;
- le fichier copié reste en lecture seule.

Si l'import échoue :

- aucune donnée partielle ne doit être conservée ;
- `collection_file_description` ne doit pas être sauvegardé ;
- le fichier copié doit être supprimé comme dans le workflow actuel.

## Migration

Aucune migration n'est attendue si `t_user.collection_file_description` existe
déjà dans le schéma courant. Si l'analyse de la tâche `00` montre un écart entre
modèle, migration et documentation, le corriger dans cette tâche.

## Tests Attendus

Ajouter ou modifier des tests backend pour valider :

- import valide avec `single_sheet_conf` ;
- import valide avec `multiple_sheets_conf.shared_layout` ;
- import valide avec `multiple_sheets_conf.sheets` ;
- sauvegarde de `collection_file_description` uniquement après succès ;
- absence de sauvegarde de `collection_file_description` si l'import échoue ;
- retour `422` lorsque la configuration est invalide ;
- les anciens codes `400`, `409`, `413` et `500` restent inchangés.

## Critères D'Acceptation

- Le controller reste limité au mapping HTTP.
- La validation de configuration est faite avant le parsing métier.
- L'import reste transactionnel.
- `GET /api/users/me/collection` n'est pas modifié.
- Les tests backend ciblés passent.
