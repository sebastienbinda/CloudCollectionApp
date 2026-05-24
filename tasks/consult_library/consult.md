Objectif :
Créer une section publique Bibliothèque permettant de consulter la base globale des jeux, plateformes et studios.

Routes frontend :
- /bibliotheque : liste les types d’entités disponibles.
- /bibliotheque/plateformes : liste les plateformes.
- /bibliotheque/studios : liste les studios.
- /bibliotheque/jeux : liste les jeux.

Endpoint backend :
- GET /api/library/entities : Retourne  le nombre d'entrée pour chaque entité :
```json
{
    "platforms" : 25,
    "studios" : 10,
    "games" : 50
}
```
- GET /api/library/platforms : Retourne la liste de plateformes de facon paginé (500 par défaut par page)
Paramètre de recherche :
 - name : recherche de type contains, sans casse et sans accents.
 - page : numéro de la page a retourner
 - size : taille de la page
 - sort : tri choix du nom de la colonne et du mode de tri example sort=name,asc
```json
{
    "page": {
        "totalElements": 10,
        "page": 0,
        "size": 500,
        "totalPages": 1
    },
    "platforms": [
        {
            "id": 1,
            "name": "platform",
            "country": "",
            "city": "",
            "creation_date": "",
            "status" : "",
            "total_games": 10
        }
    ]
}
```
- GET /api/library/studios : Retourne la liste des studios de facon paginé  (500 par défaut par page)
Paramètre de recherche :
 - name : recherche de type contains, sans casse et sans accents.
 - page : numéro de la page a retourner
 - size : taille de la page
 - sort : tri choix du nom de la colonne et du mode de tri example sort=name,asc
```json
{
    "page": {
        "totalElements": 10,
        "page": 0,
        "size": 500,
        "totalPages": 1
    },
    "studios": [
        {
            "id": 1,
            "name": "studio",
            "release_date": "",
            "manufacturer": "",
            "description": "",
            "status" : "",
            "editor_total_games": 10,
            "developer_total_games": 10
        }
    ]
}
```
- GET /api/library/games : Retourne la liste jeux de facon paginé (500 par défaut par page)
Paramètre de recherche :
 - name : recherche de type contains, sans casse et sans accents.
 - page : numéro de la page a retourner
 - size : taille de la page
 - sort : tri choix du nom de la colonne et du mode de tri example sort=name,asc
Les champs developer, editor et platform, sont les noms des entités associés (colonne name).
```json
{
    "page": {
        "totalElements": 10,
        "page": 0,
        "size": 500,
        "totalPages": 1
    },
    "games": [
        {
            "id": 1,
            "name": "game",
            "release_date": "",
            "developer": "",
            "editor": "",
            "status" : "",
            "platform": ""
        }
    ]
}
```

Règles :
- Accessible sans authentification.
- Lecture seule.
- Ne jamais exposer de données utilisateur ni de collection privée.
- Les données proviennent des tables globales de référence.
- Le menu principal affiche l’entrée Bibliothèque pour tous les visiteurs.
- La page  Bibliothèque affiche les différentes entités plateforme, studio et jeux avec un compteur indicatif. Le rendu est identique a celui des plateformes dans la page accueil avec les entités a la place des plateformes.
- Le rendu des tableau de plateformes, studio et jeux est identique a celui des tableau de collection de jeux et de wishlist.
- Chaque page d’entité propose un filtre de recherche par nom, en contains, sans casse et sans accents facon moteur de recherche au dessus du tableau.

Paramètres de pagination :
 - page : indique le numéro de la page a retourner. Commence a 0.
 - size : indique la taille  de la page, maximum ou par défaut si non précisé : 500
 - Si les paramètres sont invalides, negatif ou non fourni, les endpoints backend fallback sur  les valeurs par défaut : page=0 & size=500.

Tri des tableau :
 - Tri par défaut des endpoints sur nom et ascendent.
 - Possibilité de trier par les autres colonnes.
 - Si le tri en paramètre passé au backend n'est pas asc ou desc alors c'est asc par défaut.
 - Si la colonne demandé n'existe pas le backend realise le tri par défaut sur le nom.
 - Plusieurs tri sont autorisé, alors plusieurs paramètres sort sont passé en paramètre au endpoint de recherche.
 - Colonne de tri autorisé :
   - studio : name, release_date
   - plateform : name, country, creation_date
   - games : name, release_date, developer, plateform

Compteurs :
- La carte Plateformes affiche le nombre total de plateformes.
- La carte Studios affiche le nombre total de studios.
- La carte Jeux affiche le nombre total de jeux.
- Dans la liste des plateformes, chaque plateforme affiche le nombre de jeux associés si disponible.
- Dans la liste des studios, chaque studio affiche le nombre de jeux associés si disponible :
   - nombre de jeux en tant que editeur
   - nombre de jeux en tant que developer

Documentation :
- Créer documentation/bibliotheque.md.
- Mettre à jour documentation/site-plan.md.
- Mettre à jour documentation/backend-api.md si de nouveaux endpoints sont créés.
