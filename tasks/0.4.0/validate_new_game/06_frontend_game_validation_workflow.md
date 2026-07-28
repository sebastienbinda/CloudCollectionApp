# 06 - Workflow frontend de validation des jeux

## Objectif

Ajouter l'expérience frontend permettant à l'administrateur d'identifier,
filtrer, valider et refuser les jeux en attente, tout en gardant la
Bibliothèque publique cohérente pour les autres profils.

Cette tâche dépend de `03_backend_public_library_visibility.md`,
`04_backend_admin_game_moderation.md` et
`05_backend_admin_notifications_and_summary.md`.

## Règles Fonctionnelles

- La liste `/bibliotheque/jeux` doit permettre à `ADMIN` de filtrer par statut :
  tous, `WAITING_VALIDATION`, `ACCEPTED`.
- Les utilisateurs non admin ne doivent pas voir le filtre statut admin.
- La liste admin doit rendre visibles les jeux en attente.
- L'administrateur doit pouvoir sélectionner un ou plusieurs jeux.
- L'administrateur doit pouvoir valider la sélection après confirmation.
- L'administrateur doit pouvoir refuser la sélection après confirmation.
- Le menu doit afficher un badge ou un indicateur sur l'entrée Bibliothèque
  quand des jeux sont à valider.
- La confirmation de reset Bibliothèque doit afficher le message indiquant que
  les jeux en attente seront validés automatiquement.
- Le détail d'un jeu en attente doit rester accessible depuis la Collection du
  propriétaire grâce au Bearer optionnel.

## Périmètre Frontend

Modifier ou créer :

- les appels admin dans `LibraryAdminApi` ;
- les appels publics nécessaires dans `LibraryApi` ;
- les permissions dans `BackendRouteAccessService` ;
- les hooks `library` concernés ;
- la liste `LibraryEntityListView` ou un composant spécialisé si nécessaire ;
- le menu principal pour le badge ;
- le hook de reset pour charger et afficher le compteur admin.

## Contraintes Techniques

- Les appels publics doivent rester publics et read-only.
- Les actions protégées doivent rester dans le domaine admin frontend.
- Les pages routées doivent continuer à utiliser `PageLayout`.
- Ne pas recalculer côté frontend les règles de visibilité backend.
- Respecter les règles de `documentation/frontend-arch.md` et
  `documentation/site-plan.md`.

## Tests Attendus

Créer ou modifier les tests frontend pour couvrir :

- filtre statut visible uniquement en `ADMIN` ;
- badge Bibliothèque affiché quand le compteur est positif ;
- validation par sélection appelant l'API attendue ;
- refus par sélection appelant l'API attendue ;
- message additionnel de reset quand des jeux sont en attente ;
- absence de filtre/action admin pour `USER`, `GUEST` et anonyme.

## Critères D'Acceptation

- Le workflow admin est utilisable depuis la liste des jeux Bibliothèque.
- Les autres profils ne voient pas les contrôles admin.
- Les tests frontend ciblés passent.
- Les règles de `documentation/site-plan.md` sont respectées pour les pages
  concernées.
