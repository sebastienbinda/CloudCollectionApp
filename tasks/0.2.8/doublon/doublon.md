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


A ajouter : 

 - Apres la resolution du doublon sur l'IHM par l'admin, il faut un affichage plus visuel du resultat avec des lables et des couleurs au lieu d'afficher le json brut. Il faut un message clair qui indique si ca a marché ou si a échoué. Cet écran de résultat doit etre un écran dédié pas en dessous du formulaire de résolution. Et il doit y avoir un boutton pour retourner sur la page de détail du jeux fusionné.
 - Le bouton "Corriger un doublon" doit toujours etre visible par les admin qui peuvent donc décider de corriger un doublon non signalé
 - En tant que admin je veux un filtre sur ce flag doublon dans les critères de recherche des jeux sur la page bibliotheque jeux.
 - Je veux une tache qui vérifie une fois par jour a heure fixe configurable par défaut 4 heure du matin si des jeux ont le flag doublon a true. Si oui un mail est envoyé a l'admin pour lui indiquer le nombre de jeux en doublon a traiter et lui donnant le lien vers le site. Le  mail envoyé est un template comme pour les autres mails dans le répertoire resources.
  - Lors de la configuration des doublons, il faut prévenir par mail les utilisateurs concernés par la modification et l'impacte sur leur collection. Le  mail envoyé est un template comme pour les autres mails dans le répertoire resources.
  - Lorsque l'utilisateur signale un doublon une popup apparait indiquant ce qu'implique la signalisation et demande confirmation avant envoie au serveur du signalement. De plus, le boutton doit être visible pour les utilisateurs connectés meme si le jeu ne fait pas partie de leur collection. La seule codition pour les utilisateurs USER est qu'il ai une collection.
  - La page detail d'un jeu affiche une icone qui indique si le jeu est dans la collection de l'utilisateur courant. L'icone est basée sur celle utilisé dans le dock menu de type mobile qui ressemble a un coeur. Cette nouvelle icone est du meme style, en plus visible et avec des couleurs (rose par exemple pour un coeur). A coté ou dessous l'icone on peut ajouter un text indicatif du type "Vous posséder ce jeux"