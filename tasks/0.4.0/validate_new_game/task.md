Lors de l'import de la collection d'un utilisateur et plus précisément lors de la création de nouveau jeux dans la biblioteque, je veux que désormais il y ai un statut indiquant que le jeu doit etre validé par un  administrateur.
Le statut des jeux de la biblioteque peut donc etre :
 - WAITING_VALIDATION
 - ACCEPTED

 Le but principale de cette tache est de permettre aux utilisateurs d'importer et de voir leurs jeux sans attendre validation de l'administrateur mais que ces jeux ne soit pas visible des autres avant validation administrateurs.

 Les jeux visibles de la biblioteque ne sont que les jeux a l'état ACCEPTED. Il faut donc changer les endpoint de recherche de jeux dans la biblioteque pour ne retourner que ceux qui sont ACCEPTED pour les profiles USER ou les anonymes non authentifiés. Pour les profile ADMIN tous les jeux sont retournés.
 Toutes, les jeux de la collection ne sont pas impacté par cet état.
 Depuis la vue collection, l'utilisateur peut toujours voir la page de description d'un jeu même si le jeu est dans l'état WAITING_VALIDATION. Pour ce faire, le endpoint /api/library/games/<game_id> doit retourné 404 si le jeu est dans l'état WAITING_VALIDATION et que le jeu n'est pas dans la collection de l'utilisateur ou que l'utilisateur n'est pas connecté. Ce endpoint permet donc :
   - anonyme, USER, GUEST : voient seulement ACCEPTED, sauf USER propriétaire du jeu dans sa collection ;
   - ADMIN : voit tout

 En tant qu'administrateur, depuis la liste des jeux de la biblioteque je veux :
  - Etre informé, une fois par jour que des jeux sont a valider, de la meme manière que pour les doublons. Utiliser le même scheduler de notification quotidient pour les doublons que pour les pour les nouveaux jeux a valider.
  - pouvoir rapidement savoir qu'il y a des jeux a valider dans la biblioteque via une couleur ou un badge visible depuis le menu sur l'entrée bibliotheque.
  - pouvoir affficher les jeux en fonction de leur statut.
  - pouvoir valider un ou plusieurs jeu via un système permettant de rapidement valider tout ou parti des jeux dans cet etat.
  - pouvoir refuser un ou plusieurs jeu via un système permettant de rapidement refuser tout ou parti des jeux dans cet etat.

Valider un ou plusieurs jeux : les jeux en base de données passe à l'état ACCEPTED avec une requête SQL optimisé pour faire des updates par bloc de 500max.
Refuser un ou plusieurs jeux : Les jeux sont supprimés de la base de données et donc désassocier de la collection du ou des utilisateurs auxquels ils sont attachés. Dans ce cas un mail est envoyé aux utilisateurs impactés pour leur indiquer la liste des jeux supprimés car refusés par l'administrateur avec un message poli et bien formé. L'envoi de mail utilise le système de template comme pour les autres mails avec un fichier de template. Les suppressions sont transactionnelles pour que rien ne soit fait en cas d'erreur. Le mail envoyé, contient le nombre de jeux a valider et le lien vers la page biblioteque avec filtre sur WAITING_VALIDATION.

L'état d'un jeu de la biblioteque n'a pas d'impacte sur le rattachement d'un jeu a un jeu existant lors de l'import. Un jeu importé peut etre rattaché a un jeu de n'importe quel status.

Lors d'un reinit admin, les jeux  sont créés à l'état ACCEPTED mais un message d'information indique a l'admin avant le reset que des jeux sont en attente de validation et que cette action les validera automatiquement. Pour ce faire un compteur de jeux en attente de validation doit etre remonté pour afficher ou non le message associé.

L'import csv par un admin, créé les jeux dans l'état ACCEPTED directement.

Documentation, mettre a jour les docs associés : 
documentation/bibliotheque.md,
documentation/backend-api.md,
documentation/database.md,
documentation/site-plan.md,
documentation/authentication.md

## Découpage proposé

- `00_existing_code_analysis_and_architecture.md` : analyser l'existant,
  confirmer les contrats manquants et proposer l'architecture cible.
- `01_database_game_validation_status.md` : ajouter le statut de validation en
  base, dans le modèle ORM et les migrations.
- `02_backend_import_status_assignment.md` : appliquer le statut initial selon
  le contexte d'import utilisateur, import admin CSV ou reset Bibliothèque.
- `03_backend_public_library_visibility.md` : filtrer les routes publiques
  Bibliothèque et préserver l'accès collection aux jeux en attente.
- `04_backend_admin_game_moderation.md` : créer les endpoints admin de
  validation et refus par lots, avec notifications utilisateurs.
- `05_backend_admin_notifications_and_summary.md` : ajouter le résumé admin,
  le compteur et la notification quotidienne des jeux à valider.
- `06_frontend_game_validation_workflow.md` : ajouter les filtres, badges,
  actions de validation/refus et message de reset côté frontend.
- `07_validation_and_docker.md` : valider les tests, builds et rebuilds Docker.
- `08_documentation_updates.md` : mettre à jour les documentations concernées et
  le README si nécessaire.
