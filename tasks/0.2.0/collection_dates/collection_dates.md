Il faut ajouter quatres champs a la table t_user_collection :
 - creation_date : Date d'ajout
 - modification_date : Date de modification de l'entrée de la collection
 - deletion_date : Date de suppression de l'entrée de la collection
 - deleted : Boolean

Pour l'instant seul la creation_date est remplie durant l'import de la collection pour mettre la date courante lors de la création de chaque entrée dans la table.