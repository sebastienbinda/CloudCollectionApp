# Validation intégrée et reconstruction Docker

## Objectif

Valider l'ensemble du parcours de partage après l'intégration des sous-tâches
backend et frontend.

## Dépendances

- Sous-tâches 01 à 07 terminées.

## Périmètre

- Exécuter la suite backend complète avec `./test_backend.sh`.
- Exécuter le build frontend de production.
- Vérifier les limites de 500 lignes par fichier source et 150 lignes par
  méthode.
- Vérifier qu'aucun secret ou token brut n'est persisté ou journalisé.
- Vérifier le parcours complet : création, ouverture du lien, échange, lecture,
  masquage des prix, révocation, réponse `411`, déconnexion et retour About.
- Vérifier les trois combinaisons utiles : collection seule, wishlist seule et
  collection avec wishlist.
- Vérifier le rendu desktop et mobile avec les outils disponibles. Respecter la
  contrainte locale interdisant l'usage du navigateur intégré tant qu'il n'est
  pas restauré.
- Reconstruire les images Docker backend et web.
- Examiner `README.md` et préparer les éventuelles modifications pour la tâche
  documentaire suivante.

## Hors périmètre

- Ajout de nouveau comportement fonctionnel.
- Modification de documentation fonctionnelle, réservée à la sous-tâche 09.

## Critères d'acceptation

- Tests backend et build frontend réussis.
- Images Docker reconstruites.
- Aucun défaut de sécurité ou régression de profil détecté.
- Les limitations de validation visuelle sont explicitement rapportées.
