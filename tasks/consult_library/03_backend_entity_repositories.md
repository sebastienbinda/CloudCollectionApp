# 03 - Repositories d'entite Bibliotheque

## Objectif

Etendre les repositories d'entite existants pour lire, compter, rechercher,
trier et paginer les plateformes, studios et jeux de la base globale.

## Etapes

1. Etendre `SqlAlchemyPlatformRepository` pour la consultation publique des
   plateformes.
2. Etendre `SqlAlchemyStudioRepository` pour la consultation publique des
   studios.
3. Etendre `SqlAlchemyGameRepository` pour la consultation publique des jeux.
4. Verifier que la colonne et le modele jeu utilisent `developer`, pas
   `developper`.
5. Ajouter le comptage global des entites :
   - plateformes ;
   - studios ;
   - jeux.
6. Ajouter la liste paginee des plateformes avec `total_games`.
7. Ajouter la liste paginee des studios avec :
   - `editor_total_games` ;
   - `developer_total_games`.
8. Ajouter la liste paginee des jeux avec les noms associes :
   - `developer` ;
   - `editor` ;
   - `platform`.
9. Appliquer les regles de pagination, recherche et tri issues de la tache 02.
10. Ajouter les tests unitaires backend des repositories.

## Criteres d'acceptation

- Aucun repository Bibliotheque transverse n'est cree pour remplacer les
  repositories d'entite existants.
- Les methodes de consultation publique restent explicitement nommees et
  separees des methodes utilisees par l'import.
- Les donnees proviennent uniquement des tables globales de reference.
- Aucune donnee utilisateur, collection privee ou chemin de fichier n'est expose.
- Les listes respectent pagination, recherche et tri.
- Les compteurs sont calcules de facon deterministe.
- Les methodes publiques ajoutees sont documentees en francais.

## Validation attendue

- Lancer les tests backend ciblant les repositories.
- Lancer `./test_backend.sh` si les repositories partagent des utilitaires.
- Verifier si `documentation/database.md` doit etre mise a jour.
