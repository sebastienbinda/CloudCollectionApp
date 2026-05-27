# 04 - Services backend Bibliotheque

## Objectif

Ajouter la couche de service qui orchestre la consultation publique de la base
globale sans exposer de details SQL aux controleurs.

## Etapes

1. Creer un service metier Bibliotheque si cela respecte mieux l'architecture
   existante.
2. Injecter les repositories d'entite existants :
   - `SqlAlchemyPlatformRepository` ;
   - `SqlAlchemyStudioRepository` ;
   - `SqlAlchemyGameRepository`.
3. Exposer une methode de comptage global pour `/api/library/entities`.
4. Exposer une methode de liste paginee pour les plateformes.
5. Exposer une methode de liste paginee pour les studios.
6. Exposer une methode de liste paginee pour les jeux.
7. Normaliser les resultats au format attendu par `consult.md`.
8. Garantir que le service reste lecture seule.
9. Ajouter les tests unitaires backend du service.

## Criteres d'acceptation

- Les controleurs ne contiennent pas de logique SQL ni de calcul de compteurs.
- Le service orchestre les repositories d'entite sans dupliquer leurs requetes.
- Le service ne lit aucune donnee utilisateur ni collection privee.
- Les payloads de sortie respectent le contrat de `consult.md`.
- Les methodes publiques ajoutees sont documentees en francais.

## Validation attendue

- Lancer les tests backend ciblant le service.
- Lancer `./test_backend.sh` si le service modifie un comportement partage.
