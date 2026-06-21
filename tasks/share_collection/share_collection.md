En tant que utilisateur connecté, je veux pouvoir partager l'accès a ma collection en fournissant un lien http contenant le token temporaire de partage.
La création du lien de partage est réalisé depuis un nouvel écran, accessible depuis un encart de la page Configuration.
Ce nouvel écran demande : 
 - La durée de validité du token (entre 1 et 240 heures)
 - L'accès a la wishList : Oui/Non
 - L'acccès aux jeux de la collection : Oui/non
 - L'acccès aux informations de prix : Oui/Non

Ce nouvel écran, liste également les tokens deja partagés et donne la possibilité de les revoquer. Revoquer une token, rend invalide le token et la session des utilisateurs connectés est invalidés et les utilisteurs sont déconnectés.
Lorsqu'un token invité est invalidé, le backend renvoie un code http spécifique et l'utilisateur est déconnecté coté frontend des l'appel a un des endpoints qui renvoie ce code. Pas de vérification en long pulling pour vérification si le token est toujours valide.

Cet accès correspond a un nouveau profile "GUEST", qui n'a que les droits de consultation. Aucun ajout ou modification n'est authorisée.

Lorsqu'on est connecté en tant que "GUEST", le nom de l'utilisateur connecté est marqué "invité" et la couleur utilisée est le jaune pour l'affichage.

Les endpoints backend qui liste les jeux de la collections ne doivent renvoyer les informations de prix que si le token est configuré pour accepter de renvoyer ces informations.

La page Configuration n'est pas accessible ni aucune des sous pages.

Les pages de la collection et liste de souhaits ont un sous titre visible en desktop et mobile indiquant "
 "Collection de XXXXX" ou "Liste de souhaits de XXXX".
Lors de l'affichage des jeux d'une plateforme de la collection le sous titre est également modifié pour "Collection de XXXXX".