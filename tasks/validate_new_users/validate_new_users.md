Dans la partie dashboard, si l'utilisateur connecté est de profile ADMIN, une nouvelle section est disponible : Configuration.

Cette section permet de configurer des paramètres de l'application qui seront sauvegarder en base de données.

Nouveau endpoint backend lié a un nouveau controller AdminConfiguration

- GET api/admin/configuration
Retourne  les paramètres de configuration de la table t_configuration
```json
{
    "auto_confirm_users": false
}
```
- PUT api/admin/configration
Met a jour les champs modifiés de la configuration et fourni en paramètre de la requête
```json
{
    "auto_confirm_users": true
}
```

La nouvelle table en base de donnée t_configuration  : 
 - last_modification_date : format datetime
 - auto_confirm_users : boolean

