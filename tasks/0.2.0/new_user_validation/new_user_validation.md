L'objecftif de la tache est de mettre tout nouvel utilisateur dans un statut "WAITING_VALIDATION" qui empeche a l'utilisateur de se connecté tant que l'administrateur (l'utilisateur de profil ADMIN) n'a pas valider son enregistrement depuis l'écran de suivi des utilisateurs du dashboard admin.

Une fois validé par l'administrateur l'utilisateur recoit un mail lui indiquant que son compte a été activté par l'administrateur et lui donne un lien d'accès direct a la page de connexion.

La mail de confirmation d'email envoyé a l'utilisateur durant la procédure d'enregistrement indique désormais ce nouveau mécanisme de validation.

Lorsqu'un utilisateur essaie de se connecter alors que son statut est WAITING_VALIDATION, un message claire est affichée dans la page de connexion.

Lorsqu'un utilisateur est créé et en attente de validation administrateur, un mail soit envoyé à l'administrateur lui indiquant qu'un nouvel utilisateur attends une validation, avec un lien direct vers la page de validation de l'utilisateur. Cette page affiche alors la liste de tous les utilisateurs en attente de validation.
L'email administrateur est configuré dans le fichier .env du déploiement docker avec une nouvelle variable.