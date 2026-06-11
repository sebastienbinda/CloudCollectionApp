L'objectif de la tache est de permettre aux utilisteurs de profil ADMIN de recréer la bibliotheque du projet et donc par conséquence les collections des uttilisateurs.

Un nouvel encart dans la page configuration accessible que par les profil ADMIN permet de lancer cette action.
Un nouvel endppoint POST /api/library/reset est ajouté a un nouveau controller library_controller pour piloetr la suppression en base de données de :
 - t_game
 - t_platform
 - t_studio
 - t_user_collection
Ce endpoint accessible uniquement au profile ADMIN réalise en suite l'import de tous les fichiers utilisateurs qui ont l'information du fichier dans la table t_user. Les imports sont ordonnés par date d'enregistrement des utilisateurs dans la base. Les imports sont réalisés avec les fichiers et les conf d'import conservés en base de données dans la table t_user. L'import de chaque utilisateur doit réutiliser le service d'import existant.
Ce endpoint est asynchrone car la tache peut prendre du temps. Le endpoint rend la main directement, créé un job asycnhrone pour la tache.
Si un reset est déja en cours renvoie d'un code retour 409.
Code retour : 202 accepted.  Payload contient le job_id lancé.
```json
{
    "job_id" : 25
}
```
En cas d'echec dans la methode asynchrone : 
 - echec d'import d'un des fichiers : On passe au suivant et on log l'erreur et on ajoute l'erreur d'import du fichier de l'utilisateur dans le context en mémoire.
 - Si le fichier utilisateur n'existe plus ou est en erreur de lecture : On passe au suivant et on log l'erreur et on ajoute l'erreur d'import du fichier de l'utilisateur dans le context en mémoire.
 - collection_file_description est null ou vide : On passe au suivant et on log l'erreur et on ajoute l'erreur d'import du fichier de l'utilisateur dans le context en mémoire.
 - echec de clean bd : ajout de l'erreur au context d'import en mémoire et on arrete le reset et on revert la base de données si des changements ont été faits.
 Le context d'import contient les success et les erreurs et permet d'envoyer un mail en fin de job pour indiquer a l'admin ce qui a été bien réalisé et ce qui a échoué.
 En cas d'echec d'un ou plusieurs utilisateurs, la biblioteque est vidé et reconstruite partiellement avec les imports qui ont fonctionnés.

 En fin de reset un mail est envoyé à l'adresse mail enregistré via variable d'env pour indiquer le résultat ok ou erreur et si erreur le contexte de l'erreur.

Durant un reset, les imports des utilisateurs sont refusés. Le endpoint existant de import doit retourner un nouveau code retour 403 indiquant qu'un reset est en cours et le message est affichée à l'utilisateur. tous les endpoints liés à l'import sont impactés, upload, analyze, import configuration et reinit.

Aucun endpoint de statut pour l'instant.

Coté frontend, apres lancement si code 202 affichage d'un message indiquant que le reset est en cours. Si code 409, message indiquant qu'un reset est deja en cours.
La demande est soumise a confirmation avec un encart très visible sur la notion de descruction possible de la bibliotheque.

Documentation :
Mise a jour du biblioteque.md  pour indiquer le changement et la possibilité de reset la bibliotheque.
documentation/backend-api.md
documentation/bibliotheque.md
documentation/import.md
documentation/site-plan.md

## Sous-tâches

Les tâches doivent être réalisées dans l'ordre suivant :

1. `00_existing_code_analysis_and_contract.md`
2. `01_backend_reset_job_contract.md`
3. `02_backend_reset_persistence_and_import_orchestration.md`
4. `03_backend_import_locking.md`
5. `04_frontend_admin_configuration_action.md`
6. `05_backend_import_core_factorization.md`
7. `06_documentation_updates.md`
8. `07_validation_and_docker.md`

Chaque sous-tâche est limitée à un périmètre livrable et vérifiable. La tâche
`00` doit être réalisée en premier et produire un court rapport d'analyse dans
le dossier `tasks/0.2.2/reset_library/`.
