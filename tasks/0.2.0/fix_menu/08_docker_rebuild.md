# 08 - Rebuild Docker

## Objectif

Rebuilder les images ou services Docker impactés par les changements runtime du
frontend.

## Prérequis

- Terminer `07_frontend_validation.md`.

## Étapes

1. Identifier le service Docker concerné par le frontend, probablement `web`.
2. Rebuilder le service avec la commande Docker Compose utilisée par le projet.
3. Noter la commande exécutée.
4. Noter le résultat du rebuild.

## Critères D'Acceptation

- Le service frontend impacté est rebuildé.
- Le résultat du rebuild est connu.
- Toute erreur de rebuild est documentée avant de poursuivre.
