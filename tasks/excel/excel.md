Il faut que l'utilisateur puisse choisir le format du fichier lors de l'import : 
 - ods : garde le fonctionement actuel
 - excel : Réaliser le meme fonctionnement mais avec un reader excel au lieu d'un reader ods.

 Le code doit être modulaire pour que au niveau service on utilise des interfaces qui permette de switch d'un type a un autre.

 Il faut interface collection_file_reader_interface.

 De cette manière si un troisieme type de fichier vien a etre ajouté, il n'y aura pas d'impacte au niveau service.