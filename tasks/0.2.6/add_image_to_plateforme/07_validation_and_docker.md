# 07 - Validation finale et rebuild Docker

## Objectif

Valider l'ensemble de la fonctionnalité images de plateformes après les
modifications backend, frontend, documentation et Docker.

Cette tâche dépend de toutes les sous-tâches précédentes.

## Validations Backend

Exécuter :

```bash
./test_backend.sh
```

Valider au minimum :

- migrations et modèles ;
- upload utilisateur ;
- lecture publique des images acceptées ;
- endpoints admin ;
- route catalog ;
- notifications email ou warnings.

## Validations Frontend

Exécuter les commandes disponibles dans le projet pour :

- build frontend ;
- tests frontend s'ils existent ;
- vérification statique si configurée.

Si une validation visuelle nécessiterait le navigateur intégré, respecter la
contrainte du projet : l'outil `iab` n'est pas disponible dans ce workspace.
Reporter cette limite et s'appuyer sur les validations disponibles.

## Rebuild Docker

Comme la tâche modifie le runtime, la configuration et les volumes Docker,
reconstruire les images concernées selon les commandes du projet.

## Vérifications Manuelles Recommandées

Vérifier dans un environnement lancé :

- détail plateforme sans image ;
- upload avec un utilisateur connecté ;
- image en attente non visible publiquement ;
- acceptation par admin ;
- image acceptée visible publiquement ;
- définition d'une image `MAIN` ;
- refus d'une image et suppression disque ;
- pagination et filtres de la section admin.

## Rapport Final Attendu

Le compte rendu doit indiquer :

- les commandes exécutées ;
- les résultats ;
- les éventuelles validations non exécutées et pourquoi ;
- le statut Docker ;
- la conformité documentaire demandée par `AGENTS.md`.

## Critères D'Acceptation

- Les tests backend passent.
- Le frontend build.
- Les images Docker concernées sont reconstruites.
- Les limitations éventuelles sont clairement listées.
