# Workflow de création d'une collection 
1. L'utilisateur créé un compte
2. L'utilisateur se connecte.
3. Le  frontend  récupère les infos de la collection de l'utilisateur via un nouveau endpoint /api/users/me/collection du controler user_controller.
3. A la connexion, comme l'utilisateur n'a pas encore de fichier de collection associé en base de données, le site affiche un tutoriel indiquant que la première chose à faire est d'importer son fichier de collection.
4. L'IHM propose alors un boutton d'upload de ce fichier.
5. L'upload appel un endpoint backend dédié de user_controller /api/users/import
6. Après l'import terminé l'utilisateur est redirigé vers la page accueil.

Note : A la connexion étape 3, si l'utilisateur a deja un fichier de collection importé alors il est comme actuiellement redirigé vers la page accueil.

# Le endpoint /api/users/me/collection

Renvoie les informations sur la collection de l'utilisateur connecté (élement de la table t_user.collection_file_path)

Réponse attendue : 
```json
{
  "has_collection": true
}
```
ou  
```json
{
  "has_collection": false
}
```
# Le endpoint /api/users/import

POST /api/users/import
Format : multipart/form-data 
   -> paramètre  : collection_file
Droit d'accès : profile USER

Description :
Le endpoint d'import est lié à l'utilisateur connecté.
Ce endpoint copie le fichier de collection de l'utilisateur (ods) vers un répertoire dédié sur le serveur. Nouveau montage docker a configurer USERS_WORKSPACE monté dans /users/workspace. Le fichier est ensuite copié /users/workspace/<user_id>/<user_id>-collection.ods. 

Le  fichier est copié en mode overwrite, le nom du fichier sur disque est 'user_id-collection.ods'.
Les droits accoridé aux fichiers copié sont en lecture seule. 0440. user et group du fichier sont ceux du user de runtime du conteneur docker.
La  taille max du fichier accepté est 100Mo (configurable par .env global a tous les utilisateurs USER_COLLECTION_MAX_UPLOAD_BYTES=104857600).

Une fois copié le endpoint lit le fichier et rempli la base de données avec les informations suivants : 
- Les plateformes : 
  Ajoute les plateformes non existantes déja dans la base en se basant sur le nom de la plateforme.
  Les plateforme de l'ods qui aliment les champs en base sont ceux deja lus actuellement par le code backend.
  name : champ platform de l'ods récupéré actuellement depuis le nom de l'onglet.
  status : UNKNOWN.
  Normalisation des noms des plateformes (champ name) : trim, tout en minuscule, conservation des accents mais si une entrée existe deja avec des  accents différents on la considère équivalente.
- Les Studio :
  Ajoute les studio non existant déja dans la base en se basant sur le nom des studio.
  Les studio de l'ods qui aliment les champs en base sont ceux deja lus actuellement par le code backend.
  name : studio
  status : UNKNOWN.
  Normalisation des noms des studio (champ name) : trim, tout en minuscule, conservation des accents mais si une entrée existe deja avec des  accents différents on la considère équivalente.
- Les jeux :
  Ajoute les jeux non existant déjà dans la base en se basant sur le couple 'name' 'platform'. Les jeux sont insérés en base avec les foreignkey liés aux platform et developpeur. Pour l'instant la colonne editeur est laissé vide.
  Les jeux de l'ods qui aliment les champs en base sont ceux deja lus actuellement par le code backend.
  name : nom du jeu
  release_date : Date de sortie. Si le champs est vide ou une date invalide alors on laisse a null et on émet un warning dans les logs.
  developer : Studio (lien vers la table studio remplie au préalable)
  description : Laissé vide  pour l'instant.
  Normalisation des noms de jeux (champ name) : trim, tout en minuscule, conservation des accents mais si une entrée existe deja avec des  accents différents on la considère équivalente.
- La tables d'association des jeux de l'utilisateur : t_user_collection qui lit les jeux a cet utilisateur. Pour l'instant la colonne game_additional_name est laissé vide.  Si un jeu existe déjà en base mais pas dans t_user_collection, on crée l’association. Si l’association existe déjà, on l’ignore

Pour l'instant, seuls les onglets de plateforme sont importés on ignore accueil et liste de souhaits.

Lors de l'appel, si l'utilisateur a deja un fichier de collection associé dans sa table t_user.collection_file_path alors l'import renvoie un code http 409.

Aucun remplacement n'est autorisé en base si les informations existent deja dans ce endpoint.

L'import doit être atomique tous réussi ou tout échoue. On garde pas d'état transitoire.
En fin d'import en succès on ajoute le chemin du fichier cible en base de données dans la table t_user avec t_user.collection_file_path stockera le chemin cible complet : /users/workspace/<user_id>/<user_id>-collection.ods.
Pour le fichier copier, il est simplement supprimé si l'import échoue.

Normalisation des champs :
 - “Conservation des accents mais équivalence si accents différents” doit être formalisé. 
    - valeur stockée : trim().lower() avec accents conservés ;
    - clé de comparaison : trim().lower() + suppression des accents via Unicode normalization.

Gestion des doublon dans le fichier ods : 
 - Si un jeux, plateforme ou studio est en double (en considérant les règles de normalisation des champs), on n'importe que le premier trouvé. Les autres sont ignorés avec un log de warn mais pas d'erreur empéchant de continuer.

Réponse du endpoint : 
- 201 : en cas de succès avec :
   - le nombre de plateforme créés (qui n'existaient pas)
   - le nombre de studio créés (qui n'existaient pas)
   - le nombre de jeux créés (qui n'existaient pas)
   - Le nombre de jeux associés à la collection de l'utilisateur (tous y compris ceux qui existaient deja)
   Fromat json : 
   ```json
    {
      "created_platforms": 3,
      "created_studios": 12,
      "created_games": 42,
      "associated_games": 58
    }
   ```
- 400 : Fichier invalide. Fichier non ods, fichier illisible, fichier ne contenant pas les onglets ou colonnes attendues. fichier invalide si aucune feuille plateforme importable n’existe, ou si une feuille plateforme importable ne contient pas les colonnes attendues.
- 413 : Fichier trop volumineux.
- 403 : Utilisateur non authorisé
- 409 : Collection deja importé
- 500 : Erreur non prévue

# Architecture de code

Toutes les fonctions de lecture du fichier ODS doivent être centralisées dans un service dédié et être factorisé avec les fonction deja existantes du code backend. Le but a long terme est de pouvoir lire d'autres types de fichier en changeant uniquement le service appelée lors de l'import en fonction du type de fichier.
  