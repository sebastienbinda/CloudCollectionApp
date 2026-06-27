Que se passe t-il si plusieurs utilisateurs importe leur fichier en meme temps ? il peut y avoir des jeux dupliqués alors que le match aurai associé les  memes jeux ? Si oui, peux tu ajouter un système de lock pour éviter ce problème ?

Dans les jeux videos il y a souvent des suites genre
Final Fantasy
Final Fantasy 2
Final Fantasy III.
Il faut modifier l'algorithme de matching pour que "Final Fantasy" est un match score de 0 avec "Final Fantasy 2"
Il faut modifier l'algortithme de matching pour que "Final Fantasy 3" est un très haut score de matching avec "Final Fantasy III"


Pour les jeux durant l'import si le seuil est compris entre le seuil haut et bas, il faut :
 - Rattacher le jeux mais conserver les informations d'origines du fichier de l'utilisateur
 - L'administrateur peux ensuite depuis une page dédiée acccessible depuis un nouvel encart de la page configuration "Control des imports", refuser l'association et dans ce cas un nouveau jeux est créé et le jeu de la collection de l'utilisateur est rattaché a ce nouveau jeu créé.
Dans tous les cas si le seuil est inférieur a limite basse le jeux est créé et la plateforme refusée.
Lors du mail envoyé a l'admin en fin d'import, il faut faire apparaitre très  clairement si l'administrateur a des nouveaux a controler depuis cette nouvelle page de "Control des imports".
