En tant qu'utilisateur connecté, je veux pouvoir depuis la page "Wishlist" filtrer les jeux par "En cours d'achat" oui/non/tous.
La notion de "en cours d'achats" correspond au jeux dont soit la date d'achat soit le lieu d'achat soit le prix d'achat est défini.
Le filtrage est réalisé coté backend par le endpoint de recherche des jeux de la wishlist.
L'application du filtre est conservé dans l'url pour permettre d'y accéder directement.
Le filtrage par défaut est "Tous".

Il faut que le filtrage par défaut soit configurable pour les utilisateurs de profile GUEST lorsque l'utilisateur créé son lien de partage.
Une nouvelle configuration de token de partage est ajouté : wishlist_buy_status_default_filter. L'utilisateur peut alors choisir oui/non/tous lors de la création du lien de partage.
Ce filtre par défaut est ensuite appliqué lorsqu'un utilisateur de profile guest arrive sur la page whishlist. Il peut cependant changer ce filtre par la suite.