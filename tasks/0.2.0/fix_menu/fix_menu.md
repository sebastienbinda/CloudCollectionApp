L'objectif de la tache est de corriger les styles des bouttons des menus et leur contenu pour les rendre homogènes.
Chaque boutton doit avoir une couleur proche du vert lié à la pallète de couleur actuel.
Tous les bouttons sont des composant button et non des lien html par exemple le boutton connecion doit être conforme aux autres boutton.
L'action Connexion/Deconnexion est la dernière de la liste.

De plus il faut que se menu soit acccessible sur toutes les pages du site.
Il faut donc homogénéisé le layout des pages pour avoir un layout commun avec : 
 - Un bloc header qui contient menu, utilisateur connecté et informations sur la page (plusieurs pages on déja un bloc header, le contenu doit etre repris de l'existant).
 - Le footer
 - Le contenu de la page.
Je veux un composant React Page layout qui représente ce modele, et chaque page du site l'utilise et il faut indiquer dans le fichier agents et frontend-arch que l'on doit toujours utilisé sur layout lors de la création d'une nouvelle page.