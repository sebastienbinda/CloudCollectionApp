L'objectif de la tache est de permettre aux utilisateurs connectés de proposer par upload une image pour chaque platefome enregistrée en base de données.
Cet proposition d'ajout d'image est un boutton ajouter a la page de detail des plateformes accesible uniquement si l'utilisateur est connecté.
Ceci fait appel a un nouveau endpont backend POST /api/library/platform/{id}/image.
Ce endpoint enregistre l'image fourni dans un répertoire dédiés aux images qui est un nouveau volume du conteneur docker avec la variable BACKEND_IMG_DIR. Dans ce répertoire si il n'existe pas, un répertoire avec le nom de la plateforme est créé de type /images/platforms/{nom}. 
Vérification : La taille des images qu'il est possible d'upload est limité par configuration et var d'env.
Apres validation et copie du fichier :
 - Enregistrement en base de l'image et association a la platform via une nouvelle table t_platforms_images avec id, id de la platform, path de l'image, type de l'image, status, id user, date de creation.
 - Le type de l'image est un énumée avec deux valeurs possibles pour l'instant : MAIN, OTHER. Il ne peut y avori qu'une seule image de type MAIN.
 - Le status est un énumée pouvant etre : WAITING_VALIDATION, ACCEPTED
 - Le id user est l'identifiant de l'utilisateur qui propose l'image.
A la création l'image est enregistré avec le statut a WAITING_VALIDATION et  le type OTHER et un email est envoyé à l'admin pour lui indiquer qu'une nouvelle image est proposée par un utilisateur et qu'il doit la valider.
Retour du endpoint : 
 - 201 : created nouvele image déposé
 - 403 : forbidden si pas connecté
 - 404 : Si la plateforme n'existe pas dans le referentiel
 - 422 : Si l'image est trop volumineuse

 La page de detail d'une plateforme est mise a jour pour afficher les images qui sont au status ACCEPTED. L'image de  type MAIN représente la "vitrine" de la plateforme et doit être mise en avant. les autres images sont affichées (5max), dans un diaporama d'image. Si il n'y a pas de main on utilise la première OTHER trouvée. Si il n'y a pas de OTHER on affiche pas le diaporama. SI il n'y a aucune image on affiche aucune image ni diaporama.
 Il faut donc que le endpoint qui retourne une plateforme, retourne également la liste des liens vers les images ACCEPETED associé à la plateforme.

 Il faut ensuite, une nouvelle section dans configuration accessible que par les profils admin, pour lister, afficher et permettre d'accepter ou refuser les images proposées par les utilisateurs.
 Cettte page liste toutes les entrées de la table t_paltformes_images. affiche le  nom de la plateforme associée, le status, une  maniature de l'image, le nom de l'utilisateur qui la propose, la date de creation et propose de cliquer sur la miniature pour la voir en plus grand.
 Propose des filtres de recherche sur le statut et la plateform. Ces deux filtres sont des select list avec la liste des status et platformes possibles.
 En cas d'acceptation, le status est modifié en base a ACCEPTED,
 En cas de refus, l'image est supprimée sur disque et l'entrée en base supprimée.
 Depuis ce nouvel écran, l'admin peut aussi décider si une image est l'image de type MAIN de la platforme. Dans ce cas, le type en bd est modifié après avoir passer les autres images de la plateforme en OTHER si il y en avait deja une en MAIN.
 Nouveau endpoint backend de modification d'une image PUT /api/library/platform/{id}/image/{id}/{type}
 - 200 : updated success
 - 404 : image ou platforme inconnue
 - 403 : access refusé car user non connecté


