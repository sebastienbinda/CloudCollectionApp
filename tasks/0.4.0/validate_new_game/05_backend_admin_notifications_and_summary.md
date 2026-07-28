# 05 - Résumé admin, badge et notification quotidienne

## Objectif

Fournir au frontend et aux emails admin les informations nécessaires sur les
jeux en attente de validation.

Cette tâche dépend de `04_backend_admin_game_moderation.md`.

## Règles Fonctionnelles

- L'administrateur doit pouvoir connaître le nombre de jeux
  `WAITING_VALIDATION`.
- Le frontend doit pouvoir afficher un badge ou une couleur sur l'entrée
  Bibliothèque du menu quand ce nombre est supérieur à zéro.
- La confirmation de reset Bibliothèque doit afficher un message additionnel
  quand des jeux sont en attente de validation.
- L'administrateur doit recevoir une notification quotidienne quand au moins un
  jeu est en attente.

## Périmètre Backend

Implémenter :

- un endpoint protégé `ADMIN` de résumé de validation des jeux ;
- un service de comptage des jeux en attente ;
- une notification quotidienne basée sur le modèle existant des notifications
  de doublons ;
- un template email dédié ;
- l'enregistrement du scheduler au démarrage applicatif si la base est
  configurée.

## Contraintes Techniques

- Ne pas envoyer de notification si le compteur est à zéro.
- Si `ADMIN_NOTIFICATION_EMAIL` est absent, logguer un warning sans bloquer
  l'application.
- Le résumé admin ne doit pas être public.
- Les routes publiques Bibliothèque doivent rester consultables sans Bearer.

## Tests Attendus

Créer ou modifier les tests backend pour couvrir :

- compteur à zéro ;
- compteur supérieur à zéro ;
- endpoint résumé protégé `ADMIN` ;
- refus d'accès `USER` et anonyme ;
- notification quotidienne envoyée seulement si nécessaire ;
- warning quand l'email admin est absent ;
- scheduler initialisé dans les conditions attendues.

## Critères D'Acceptation

- Le backend expose un compteur admin exploitable par le frontend.
- La notification quotidienne fonctionne selon la configuration.
- Les tests backend ciblés passent.
