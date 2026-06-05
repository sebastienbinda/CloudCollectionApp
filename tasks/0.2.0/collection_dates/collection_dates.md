Il faut ajouter quatres champs a la table t_user_collection :
 - creation_date : Date d'ajout non null
 - modification_date : Date de modification de l'entrée de la collection. Peut etre null.
 - deletion_date : Date de suppression de l'entrée de la collection. Peut etre null.
 - deleted : Boolean. Fase par défaut

Pour l'instant durant l'import :
 - la creation_date est remplie pour mettre la date courante lors de la création de chaque entrée dans la table.
 - deleted est positionné a false.

Cette modification n'impacte pas le reader ods et doit etre mis en place au niveau de la couche générique qui ne dépend pas du type de fichier importé.
