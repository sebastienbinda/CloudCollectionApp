# 05 - Validation et Docker

## Objectif

Valider l'ensemble de la fonctionnalité après implémentation.

Cette tâche dépend de :

- `04_documentation_updates.md`

## Tests Backend

Lancer :

```bash
./test_backend.sh
```

Les tests doivent couvrir au minimum :

- route protégée ;
- succès de réinitialisation ;
- absence de collection ;
- fichier disque absent accepté ;
- rollback SQL en cas d'échec ;
- non-régression du statut `GET /api/users/me/collection`.

## Build Frontend

Lancer :

```bash
cd frontend
npm run build
```

Vérifier que la page Configuration compile et que les props ajoutées sont bien
routées depuis le view-model.

## Validation Manuelle

Scénario minimal :

1. se connecter avec un utilisateur `USER` ayant une collection ;
2. ouvrir `/configuration` ;
3. annuler la confirmation et vérifier qu'aucun appel n'est envoyé ;
4. confirmer la réinitialisation ;
5. vérifier la redirection vers `/collection/import` ;
6. vérifier que `GET /api/users/me/collection` retourne
   `{"has_collection": false}` ;
7. vérifier que l'ancien fichier de collection n'est plus présent quand il
   existait.

## Docker

Comme la fonctionnalité modifie le comportement runtime backend et frontend,
reconstruire les images Docker affectées selon la procédure du projet.

## Rapport Final

Le rapport final doit indiquer :

- tests lancés et résultats ;
- build frontend lancé et résultat ;
- rebuild Docker lancé ou raison si non lancé ;
- état de mise à jour de `README.md` ;
- conformité documentaire avec une ligne par fichier concerné.
