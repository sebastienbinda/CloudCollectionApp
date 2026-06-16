Dans le menu desktop et dans le dock mobile, il faut mettre en surbrilance l'entrée du menu qui correspond a la page courante. Il faut réutiliser le vert clair de la palette de couleur du site.

Une icone doit toujours correspondre a la page de navigation courante sans ajouter d'entrées dans le menu

## Résultat Branche `menu_highlight` - 2026-06-16

La tâche est réalisée.

Changements appliqués :

- `AppViewSwitch` calcule l'entrée de menu active depuis la vue courante.
- `PageLayout` transmet cette clé active au menu partagé et déduit aussi
  l'entrée active depuis l'URL courante quand une page ne relaie pas cette clé.
- `MainMenu` applique `aria-current="page"` et la classe active sur les boutons
  desktop, dock mobile et actions secondaires.
- Le bouton mobile `Plus` est surligné quand la page active correspond à une
  action secondaire masquée derrière ce panneau.
- Les styles utilisent un vert plus sombre et moins saturé (`#dbeadf`,
  `#9fbea9`, `#166534`, `#15803d`).
- `documentation/menu.md` documente la règle de surbrillance.

Correspondances retenues :

- pages Bibliothèque, listes Bibliothèque, détails plateforme/jeu Bibliothèque :
  `Bibliotheque` ;
- pages collection, détail plateforme collection, détail jeu collection,
  import et ajout : `Ma collection` ;
- utilisateurs : `Configuration` ;
- authentification : `Connexion` ;
- à propos : `A propos` ;
- wishlist : `Liste de souhaits`.

Validations :

- `npm run build` depuis `frontend/` : OK.
- `git diff --check` : OK.
- `docker compose -f docker/docker-compose.local.yml build web` : OK.
