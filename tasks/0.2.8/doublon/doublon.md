Je veux deux nouvelles actions sur la ficher de description du detail d'un jeu:
 - "Indiquer un doublon" : 
     - bouton accessible aux utilisateurs connectés ayant une collection (pas aux utilisateurs GUEST)
     - Ce boutton permet d'ajouter un flag true en base de donnée dans la table "doublon_flag" sur la table t_game.
     - Apres modification du jeu coté backend, une popup informe l'utilisateur en le remerciant de sa contribtion et lui informe qu'un administrateur vérifira sa demande.
     - Le boutton est masqué si le jeu a deja le flag "doublon_flag"
 - "Corriger un doublon" : boutton accessible au profile ADMIN
     - Ce boutton n'apparait que si le jeu a le flag "doublon_flag" sur la table t_game
     - En cliquant dessus, une nouvelle page apparait pour gérer le doublon. Cette nouvelle page propose deux chois :
        - Refuser le doublon : dans ce cas, on remet de flag doublon_flag à false apres confirmation et on retourne sur la page de detail du jeu.
        - Choisir parmis une liste des jeux de la même plateforme le jeu auquel le doublon est rattaché, choisir via une case a choché si on veut conservé le nom comme alias du nom du jeu d'origine et accepter la demande. La liste est une liste déroulante avec une recherche textuelle possible pour filtrer les résultats. Après sélection du jeux on propose a l'ihm une comparaison des attributs des deux jeux avec possibilité de choisir quel valeur on veu garder. On envoie toutes ces informations sur un nouveau endpoint backend d'accès ADMIN uniquement de gestion des doublons : POST /api/library/games/doublon. Ce endpoint réalise : 
            - Suppression du jeu en doublon
            - Modification si nécessaire des attributs du jeu d'origine avec les valeurs des attributs choisis
            - Ajout du nom du jeu considéré comme doublon alias du nom du jeu dans une nouvelle table dédiée.
            - Association au jeu restant, des jeux deja associé dans la collection des utilisateurs dans la table t_user_collection
            - Retour json avec les informations de ce qui a été fait avec le nombre d'utilisateur pour qui le jeu a été remappé sur le jeux restant et le temps de traitement.
        Après retour success ou erreur du backend affichage du resultat retourné.