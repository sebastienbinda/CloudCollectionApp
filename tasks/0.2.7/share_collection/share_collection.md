En tant que utilisateur connecté, je veux pouvoir partager l'accès a ma collection en fournissant un lien http contenant le token temporaire de partage.

Le lien avec le token invité est /collection/share/<token>. Coté frontend, lorsque l'on arrive sur cette page, le token dans l'url est remplacé par un token de session et redirige l'utilisateur vers la page collection en retirant le token de l'url.

La création du lien de partage est réalisé depuis un nouvel écran, accessible depuis un encart de la page Configuration.
Ce nouvel écran demande : 
 - La durée de validité du token (entre 1 et 240 heures)
 - L'accès a la wishList : Oui/Non
 - L'acccès aux jeux de la collection : Oui/non
 - L'acccès aux informations de prix : Oui/Non

Ce nouvel écran, liste également les tokens deja partagés et donne la possibilité de les revoquer. Revoquer une token, rend invalide le token et la session des utilisateurs connectés est invalidés et les utilisteurs sont déconnectés.
Ce nouvel écran affiche la liste des partage créés avec :
 - date de création ;
 - date d’expiration ;
 - permissions ;
 - statut actif, expiré ou révoqué ;
 - Bouton pour recopier dans le presse papier le lien  ;
Les partage expirés sont visible avec une encart rouge autour de la ligne re présentant le partage dans la liste.
Il faut bien penser a avoir un rendu mobile dédié.

Seul le propriétaire d'un partage peut lister et revoquer ses partages.

Lorsqu'un token invité est invalidé, le backend renvoie un code http spécifique 411 et l'utilisateur est déconnecté coté frontend des l'appel a un des endpoints qui renvoie ce code. Pas de vérification en long pulling pour vérification si le token est toujours valide.Un token est invalidé si :
 - token expiré
 - token revoqué par l'utilisateur qui a partagé le lien
 - utilisateur ayant partagé le lien supprimé , vérouillé.
Les tokens expirés ne sont pas supprimés

Le partage est conservé même si l'utilisateur :
- réinitialise sa collection ;
- change de pseudonyme ;
La partage est revoqué si l'utilisateur :
- est verrouillé ou supprimé

Les claims du toekn GUEST sont :
les claims, par exemple :
- profile: GUEST ;
- identifiant du partage ;
- identifiant du propriétaire ;
- pseudonyme du propriétaire ;
- permissions accordées.

Cet accès correspond a un nouveau profile "GUEST", qui n'a que les droits de consultation. Aucun ajout ou modification n'est authorisée. Les actions de modifications sont désactivté coté frontend mais aussi interdite coté backend.
Les droits d'accès en tant que GUEST sont :
 - collection autorisée (partiellement avec ou sans les informations de prix)
 - wishlist autorisée (partiellement avec ou sans les informations de prix)
 - détail d’un jeu autorisée (partiellement avec ou sans les informations de prix)
 - détail d’une plateforme  autorisée (pas  autorisé a ajouter des images)
 - statistiques globales et par plateforme autorisée
 - recherche et filtres autorisés
 - téléchargement du fichier ODS interdit.

Si l'utilisateur GUEST n'est pas autorisé a voir les informations de prix alors sont masqués :
 - purchase_price et price_unit
 - sommes et moyennes des prix

Lorsqu'on est connecté en tant que "GUEST", le nom de l'utilisateur connecté est marqué "invité de XXX" et la couleur utilisée est le jaune pour l'affichage et le XXX est le pseudonyme de l'utilisateur qui a partagé sa collection.

La page "Configuration" est masqué pour les utilisateurs GUEST.
La page "Collection" est masquée si non autorisé avec le profile GUEST.
La page Wishlist est masquée si non autorosiée avec le profile GUEST
Les pages Bibliothèque et À propos reste toujours visibles car publiques.

Après revokation de son token, le GUEST est déconnecté et redirigé vers la page "A propos".

Les endpoints backend qui liste les jeux de la collections ne doivent renvoyer les informations de prix que si le token est configuré pour accepter de renvoyer ces informations.

La page Configuration n'est pas accessible ni aucune des sous pages.

Les pages de la collection et liste de souhaits ont un sous titre visible en desktop et mobile indiquant "Collection de XXXXX" ou "Liste de souhaits de XXXX". Ce format n'est affiché que pour les utilisateurs de profil GUEST.
Lors de l'affichage des jeux d'une plateforme de la collection le sous titre est également modifié pour "Collection de XXXXX".
Avec XXXX est le pseudonyme de l'utilisateur qui partage sa collection.

Documentation : 
La documentation users.md doit etre mise à jour pour préciser le nouveau role GUEST.
Une page share.md doit etre créé pour expliquer de faocn consive a destination des agents IA, le fonctionnement du partage de collection. Ce fichier doit ensuite être ajouté dans le AGENTS.md pour être pris en compte lors des verifications de spec dans la section "Change Governance".

## Découpage de réalisation

Les sous-tâches doivent être réalisées dans l'ordre suivant :

1. [Persistance des partages](01_database_share_persistence.md)
2. [Profil GUEST et échange du lien](02_backend_guest_authentication.md)
3. [API de gestion des partages](03_backend_share_management_api.md)
4. [Consultation de collection par un invité](04_backend_guest_collection_access.md)
5. [Activation de la session invitée](05_frontend_guest_session.md)
6. [Écran de gestion des partages](06_frontend_share_management.md)
7. [Navigation et vues GUEST](07_frontend_guest_views.md)
8. [Validation intégrée et Docker](08_validation_and_docker.md)
9. [Documentation du partage](09_documentation.md)

Chaque sous-tâche doit rester limitée à son périmètre. Les tests ciblés sont
réalisés avec la sous-tâche qui introduit le comportement correspondant.
