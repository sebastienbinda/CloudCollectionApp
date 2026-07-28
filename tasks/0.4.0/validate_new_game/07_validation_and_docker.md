# 07 - Validation finale et rebuild Docker

## Objectif

Valider l'ensemble de la fonctionnalité après les modifications backend et
frontend.

Cette tâche dépend de toutes les sous-tâches de code précédentes.

## Validations Backend

Exécuter depuis la racine du projet :

```bash
./scripts/test_backend.sh
```

Valider au minimum :

- migration et modèle `Game.status` ;
- import utilisateur en `WAITING_VALIDATION` ;
- import admin CSV et reset en `ACCEPTED` ;
- filtrage public Bibliothèque ;
- accès propriétaire aux jeux en attente depuis Collection ;
- endpoints admin de validation/refus ;
- emails utilisateurs après refus ;
- compteur admin et notification quotidienne ;
- route catalog et protections de profil.

## Validations Frontend

Exécuter depuis `frontend` :

```bash
npm test
```

Exécuter aussi le build configuré du frontend si distinct des tests.

Valider au minimum :

- filtres admin ;
- sélection et actions de lot ;
- badge menu ;
- message de reset ;
- absence des contrôles admin hors profil `ADMIN`.

## Rebuild Docker

Comme la tâche modifie le runtime backend, frontend et le schéma PostgreSQL,
reconstruire les images Docker concernées selon les commandes du projet.

## Vérifications Manuelles Recommandées

Vérifier dans un environnement lancé :

- import utilisateur créant un nouveau jeu en attente ;
- jeu visible dans la collection de l'utilisateur ;
- jeu masqué dans la Bibliothèque anonyme ;
- jeu visible dans la Bibliothèque admin avec filtre statut ;
- validation admin rendant le jeu public ;
- refus admin supprimant le jeu des collections et envoyant l'email ;
- reset admin affichant le message si des jeux sont en attente.

Si une validation visuelle nécessiterait le navigateur intégré, respecter la
contrainte du projet : l'outil `iab` n'est pas disponible dans ce workspace.
Reporter cette limite et s'appuyer sur les validations disponibles.

## Rapport Final Attendu

Le compte rendu doit indiquer :

- les commandes exécutées ;
- les résultats ;
- les éventuelles validations non exécutées et pourquoi ;
- le statut Docker ;
- les limitations connues.

## Critères D'Acceptation

- Les tests backend passent.
- Les tests frontend passent.
- Le frontend build.
- Les images Docker concernées sont reconstruites.
- Les limitations éventuelles sont clairement listées.
