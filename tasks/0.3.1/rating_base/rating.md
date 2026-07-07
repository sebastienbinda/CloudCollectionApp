Le but de la tache est de standardisé le système de notation des jeux de l'utilisateur.
Pour se faire, il faut demander dans le formulaire d'importation la base de notation. Un nouveau champ global non lié a un onglet en particulier.
Cette information est globale et non dépendante du type de fichier.
Cette information est ensuite sauvegardé en base dans le json de configuration de l'import.
IL faut ensuite ajouter la possibilité de mapper lors de l'import la colonne correspondant a la note dans le fichier importé par l'utilisateur.  Ceci dans tous les formats.
Deux nouveaux champs sont ajoutés a la table t_user_collection nommé rate et rate_normalized qui est remplie lors de l'import avec :
 - rate : la note en string telle qu'inscrite dans le fichier
 -rate_normalized : la standardisation de la note en un entier base 100 arrondie a l'entier l inférieur. La normalisation prend en charge que la note peut etre soit un entier directement soir une string de type <rate>/<base> exemple 08 ou 8 ou 08/10 ou 8/10 si la base est 10.

 Ensuite sur le endpoint statistics on doit remonter les jeux qui ont plus de 90 de rate_normalized et appliquer le filtre selectionner sur la plateforme si il y en a un.