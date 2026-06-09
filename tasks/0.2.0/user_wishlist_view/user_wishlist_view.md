Les utilisateurs connectés peuvent désormais consulter les jeux de leur wishlist depuis une entrée du menu dédiée "Liste de souhaits". Cette nouvelle entrée du menu est cachée (disabled) si l'utilisateur n'est pas connecté. L'entrée du menu est placé dans le menu de facon cohérente avec menu.md.
Cette nouvelle page wishlist présente la liste des jeux dont le flag wishlist=true.
Le rendu est identique a la page collection par plateforme avec la différence qu'une colonne "plateforme" est ajoutée. La page collection est spécifique a une plateforme alors que la nouvelle page liste les jeux de toutes les plateformes. La nouvelle colonne  "plateforme" est uniquement une information, pas de lien vers la page listant les plateformes. La nouvelle page n'a pas de selecteur de plateforme et pas d'actions.
Les colonnes a afficher sont :
 - Nom du jeu
 - Plateforme
 - Studio
 - Date de sortie
 - Version

 Les autres champs présent dans page plateforme ne sont pas utiles ici.

Cette page affiche également des filtres sur :
- Plateforme.
Cette page permet le tri nom, plateforme, studio, date de sortie.
Par défaut les entrées du tableau sont triés sur le nom par ordre alphabétique

Il faut donc centraliser les composants react qui affiche la collection (plateformes et jeux) avec un paramètre de conf wishlist et utiliser ce composant commun dans les deux écrans, collection et wishlist.

Pas de nouveau endpoint backend. On réutilise l'existant.
Seul le code frontend et la documentation sont touchées.

Nouvelle route frontend : /wishlist

## Découpage en sous-tâches

1. `00_existing_code_analysis_and_architecture.md` : analyser le frontend
   existant, les contrats documentés et produire le rapport d'architecture
   cible avant toute modification applicative.
2. `01_frontend_contract_and_navigation.md` : cadrer et implémenter la route
   `/wishlist`, l'entrée de menu et l'intégration dans l'orchestration de
   navigation.
3. `02_frontend_shared_collection_components.md` : centraliser les composants
   React réutilisables entre la page plateforme et la page wishlist.
4. `03_frontend_wishlist_data_and_table.md` : charger les jeux wishlist avec
   `wishlist=true` et afficher le tableau avec colonnes, filtre et tris
   attendus.
5. `04_backend_sorting_contract.md` : appliquer le tri backend pour les listes
   de jeux collection et wishlist, et demander l'ajout de cette règle dans
   `frontend-arch.md` et `backend-arch.md`.
6. `05_documentation_and_validation.md` : mettre à jour la documentation et
   valider le périmètre frontend.
