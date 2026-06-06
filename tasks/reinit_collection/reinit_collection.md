En tant qu'utilisateur connecté avec le role USER je veux pouvoir avoir une action depuis
 la page "Configuration" qui propose "Reinitialiser la collection".

 Cette action fait appel au backend sur POST /api/users/collection/reinit.

 Cette action permet de supprimer toutes les entrées de la table t_user_collection pour le user connecté.
 Cette action supprime également le fichier de collection associé à l'utilisateur sur disque ainsi que le chemp associé dans t_user en base de données.
 Le endpoint bakcend est entièrement transactionnel au niveau bd. Si une action échoue tout est rollback.
 Code retour : 
  - 200 : Si succès
  - 404 : Si l'utilisateur n'a pas de collection
  - 500 : Si une erreur c'est produite
NOTE :  Si le fichier sur disque n'existe pas, cela ne fait pas échouer la fonction mais un log de warning est levé.

 Une fois l'action réalisée, le frontend redirige sur la page onboarding car l'utilisateur n'a plus de collection, 
 avec le meme test qui existe deja pour les autres pages.

 La section coté frontend sur le Configuration :
  - Explique le but de cette fonctionnalité qui est de supprimer la collection actuelle pour pouvoir en importer une nouvelle.
  - Demande confirmation de reinitialisation avant soumission au backend.

 