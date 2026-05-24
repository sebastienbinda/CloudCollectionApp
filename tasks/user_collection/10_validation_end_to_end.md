# 10 - Validation end-to-end

## Objectif

Valider le workflow complet de création et d'import de collection utilisateur.

## Étapes

1. Lancer les tests backend.
2. Lancer les tests frontend s'ils existent.
3. Lancer le build frontend.
4. Vérifier que les images Docker sont reconstruites si le runtime a changé.
5. Tester manuellement le workflow complet :
   - création d'un utilisateur
   - connexion
   - détection de l'absence de collection
   - affichage de l'onboarding
   - upload du fichier ODS
   - import réussi
   - redirection accueil
   - deuxième import refusé
6. Vérifier les données en base :
   - plateformes créées
   - studios créés
   - jeux créés
   - associations utilisateur créées
   - `t_user.collection_file_path` renseigné
7. Vérifier le fichier sur disque :
   - emplacement attendu
   - nom attendu
   - droits `0440`

## Critères d'acceptation

- Le workflow complet fonctionne pour un utilisateur sans collection.
- Le workflow existant reste inchangé pour un utilisateur avec collection.
- Les erreurs principales sont correctement retournées et affichées.
- Les tests automatisés passent.
- Les impacts documentaires ont été vérifiés.

## Validation attendue

- Fournir le résultat des commandes de test et build.
- Fournir un résumé des vérifications manuelles réalisées.
- Fournir le rapport de conformité documentaire demandé par `AGENTS.md`.
