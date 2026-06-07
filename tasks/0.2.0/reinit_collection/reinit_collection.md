En tant qu'utilisateur connecté avec le role USER je veux pouvoir avoir une action depuis
 la page "Configuration" qui propose "Reinitialiser la collection".

 Cette action fait appel au backend sur POST /api/users/collection/reinit.

 Cette action permet de supprimer toutes les entrées de la table t_user_collection pour le user connecté.
 Cette action supprime également le fichier de collection associé à l'utilisateur sur disque ainsi que le champ associé dans t_user en base de données. Si le fichier n'existe pas, aucune erreur n'est levée et l'action continue.
 Le endpoint bakcend est entièrement transactionnel au niveau bd. Si une action échoue tout est rollback.
 Code retour : 
  - 200 : Si succès. {"reinitialized": true}
  - 404 : Si l'utilisateur n'a pas de collection. si collection_file_path est NULL et si il n'existe aucune entrées dans la table t_user_collection. {"error": "Collection introuvable."}
  - 500 : Si une erreur c'est produite. {"error": "Unable to reinitialize collection."}
NOTE :  Si le fichier sur disque n'existe pas, cela ne fait pas échouer la fonction mais un log de warning est levé.

 Une fois l'action réalisée, le frontend redirige sur la page onboarding car l'utilisateur n'a plus de collection, avec le meme test qui existe deja pour les autres pages.

	 La section coté frontend sur le Configuration :
	  - Explique le but de cette fonctionnalité qui est de supprimer la collection actuelle pour pouvoir en importer une nouvelle. Le message explique aussi que cela supprime du serveur le fichier de collection.
	  - Demande confirmation de reinitialisation avant soumission au backend.

## Sous-tâches

Les tâches doivent être réalisées dans l'ordre suivant :

1. `00_existing_code_analysis_and_contract.md`
2. `01_backend_reinit_contract.md`
3. `02_backend_reinit_service_and_persistence.md`
4. `03_frontend_configuration_reinit_action.md`
5. `04_documentation_updates.md`
6. `05_validation_and_docker.md`

Chaque sous-tâche est volontairement limitée à un périmètre simple. La tâche
`00` doit être réalisée en premier et produire un court rapport d'analyse dans
le dossier `tasks/0.2.0/reinit_collection/`.

 
