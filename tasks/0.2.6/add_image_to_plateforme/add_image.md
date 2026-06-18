L'objectif de la tache est de permettre aux utilisateurs connectés de proposer par upload une image pour chaque platefome enregistrée en base de données.
Cet proposition d'ajout d'image est un boutton ajouter a la page de detail des plateformes accesible uniquement si l'utilisateur est connecté.
Ceci fait appel a un nouveau endpont backend POST /api/library/platforms/{id}/image. le champ multipart est "image".
Ce endpoint enregistre l'image fourni dans un répertoire dédiés aux images qui est un nouveau volume du conteneur docker avec la variable BACKEND_IMG_DIR. Dans ce répertoire si il n'existe pas, un répertoire avec le nom de la plateforme est créé de type /images/platforms/{slug nom}. L'image est enregistré avec le nom d'origine du fichier upload. Si le fichier existe deja, on ajoute un compteur en suffix.
Vérification : La taille des images qu'il est possible d'upload est limité par configuration et var d'env avec la nouvelle variable PLATFORM_IMAGE_MAX_UPLOAD_BYTES.
Apres validation et copie du fichier :
 - Validation du format de l'image : Les formats acceptés sont définis : jpg/jpeg, png, webp, gif. Il faut vérifier le MIME et l’extension.
 - Enregistrement en base de l'image et association a la platform via une nouvelle table t_platform_image avec id, id de la platform, path de l'image en absolu, type de l'image, status, user_id, date de creation.
 - Le type de l'image est un énumée avec deux valeurs possibles pour l'instant : MAIN, OTHER. Il ne peut y avori qu'une seule image de type MAIN. il faut une contrainte d'unicité bd sur le couple id/type=MAIN.
 - Le status est un énumée pouvant etre : WAITING_VALIDATION, ACCEPTED
 - Le user_id est l'identifiant de l'utilisateur connecté qui propose l'image. Il est dérivé du token backend au moment de l'insertion et ne doit pas être fourni par le frontend.
A la création l'image est enregistré avec le statut a WAITING_VALIDATION et  le type OTHER et un email est envoyé à l'admin pour lui indiquer qu'une nouvelle image est proposée par un utilisateur et qu'il doit la valider. Si l'email admin n'est pas configuré, un warning est loggé.
Retour du endpoint : 
 - 201 : created nouvele image déposé
 - 403 : forbidden si pas connecté
 - 404 : Si la plateforme n'existe pas dans le referentiel
 - 422 : Si l'image est trop volumineuse

 La page de detail d'une plateforme est mise a jour pour afficher les images qui sont au status ACCEPTED. Cette page reste d'accès public ainsi que l'accès aux images. Seul l'upload est limité au utilisateurs connectés.
 Le endpoint de récupération d'un plateforme GET /api/library/platforms/{id} est modifié pour retourner la liste des images de status ACCEPTED associées avec : id de l'image, type de l'image. grace a ces informations on peut reconstruire le lien d'acccès a l'image pour son affichage.
 Un nouveau endpoint d'accès aux images est mis en place GET /api/library/platforms/{id}/image/{id}. Ce endpoint retourne :
  - 200 si l'image existe et est accessible et retourne l'image dans le corp de la réponse
  - 404 si l'image n'existe pas ou est inaccessible.
Ce endpoint doit permettre de bypass le cache navigateur si l'image a changé via un cache-busting.

 L'image de  type MAIN représente la "vitrine" de la plateforme et doit être mise en avant. les autres images sont affichées (5max), dans un diaporama d'image. Si il n'y a pas de main on utilise la première OTHER trouvée. Si il n'y a pas de OTHER on affiche pas le diaporama. SI il n'y a aucune image on affiche aucune image ni diaporama.


 Il faut ensuite, une nouvelle section dans configuration accessible que par les profils admin, pour lister, afficher et permettre d'accepter ou refuser les images proposées par les utilisateurs.
 Cettte page liste toutes les entrées de la table t_paltformes_images. affiche le  nom de la plateforme associée, le status, une  maniature de l'image, le nom de l'utilisateur qui la propose, la date de creation et propose de cliquer sur la miniature pour la voir en plus grand. La  miniature est l'image originale redimensionné coté frontend.
 Propose des filtres de recherche sur le statut et la plateform. Ces deux filtres sont des select list avec la liste des status et platformes possibles.
 La liste des images est paginée, en réutilisant le composant tableau commun utilisé pour afficher les listes paginés.
 En cas d'acceptation, le status est modifié en base a ACCEPTED,
 En cas de refus, l'image est supprimée sur disque et l'entrée en base supprimée.
 Depuis ce nouvel écran, l'admin peut aussi décider si une image est l'image de type MAIN de la platforme. Dans ce cas, le type en bd est modifié après avoir passer les autres images de la plateforme en OTHER si il y en avait deja une en MAIN.
 Nouveau endpoint backend de modification d'une image PUT /api/library/platforms/{id}/image/{id}/type/{type} accessible aux users connectés de profil ADMIN
 - 200 : updated success
 - 404 : image ou platforme inconnue
 - 403 : access refusé car user ADMIN non connecté.
Nouveau endpoint backend de validation d'une image PUT /api/library/platforms/{id}/image/{id}/status/{status} avec status pouvant etre accepted ou refused. le  cas refused n'est pas un status DB car apres refus l'entrée est supprimée de la base.
 - 200 : updated success (meme en cas de suppression)
 - 404 : image ou platforme inconnue
 - 403 : access refusé car user non connecté
Nouveau endpoint backend pour lister toutes les images GET /api/library/platforms/images  accessible aux users ADMIN. Ce endpoint est paginé comme les endpoints de liste des jeux par exemple, il faut réutiliser un objet comun pour la structure de la pagination avec les mêmes paramètres de pagination et meme format de réponse.
 - 200 : success
 - 403 : access refusé car user non ADMIN

Documentation : 
Mettre a jour : 
documentation/backend-api.md
documentation/authentication.md : Accès public aux images ACCEPTED authorisé
documentation/database.md
documentation/site-plan.md
documentation/frontend-arch.md
documentation/backend-arch.md
README.md
 

