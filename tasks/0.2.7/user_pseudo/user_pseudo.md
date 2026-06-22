Lors de l'inscription un utilisateur doit pouvoir préciser un pseudonyme.
Il faut que ce pseudonyme indique que se nom sera cellui qui sera utilisé pour indiquer l'utilisateur connecté et pour la fonction de partage de collection.
Ce pseudonyme est enregistré en base de donnée et sera utilisé pour indiquer l'utilisateur connecté dans le header de la page. Actuellement c'est l'adresse mail qui est utilisé mais il faut désormais afficher le pseudo.
Ce pseudonyme doit etre unique en base de données,
Si le pseudonyme existe deja, il faut refuser la création du compte.
La vérification d'unicité du pseudonyme choisi est réalisé dès qu'on perd le focus sur la zone de saisie. Si la validation est refusée, le bouton de création du compte est desactivé.