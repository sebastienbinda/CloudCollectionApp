En tant  qu'utilisateur connecté, je veux pouvoir depuis chaque jeu de ma wishlist consulter les offres de ventes récentes du jeu sur les sites marchands type le bon coin, Ebay, Rakuten. Cette fonctionnalité doit etre accessible aux utilisateurs de profiles USER et GUEST.

Je veux une page avec un onglet par plateforme de vente.
Sur chaque onglet un liste des 10 annonces les plus cohérentes et triées par prix de vente avec les moins cher en premier.
Je veux un lien pour pouvoir voir chaque annonce indisivudellement
Je veux un lien au dessus du tableau pour aller sur le site marchand et aplliquer la recherche du jeu courant.

Je veux que la recherche passe par le backend python avec une nouvelle route accesibles aux profiles USER et GUEST.
/wishlist/onlinesearch?type=<Leboncoin>&game_id=<game_id>&size=<size>
Ce endpoint renvoie les informations des annonces en json avec un format unifié pour toutes les plateformes de recherche du type :
```json
{
    "results": [
        {
            "link" : "le lien http de l'annonce",
            "Title" : "Le titre de l'annonce",
            "Price" : "Le prix de vente",
            "Date" : "La date de mise en ligne de l'annonce",
            "seller": "Le nom du vendeur",
            "image": "Image principale du produit mis en vente"
        }
    ]
}
```

Si une  ou plusieurs informations sont manquante pour le revendeur demandé, l'information est laissée vide.
Il faut a minima avoir récupéré "Title", "Prix" et "Link" pour qu'une annonce soit retournée.
On ne renvoie que 50 annonces maximum et si précisé, le nombre d'annonces retorunée est égale au pramètre size fourni a la requete.