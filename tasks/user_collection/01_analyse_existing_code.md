# 01 - Rapport d'analyse du code existant

## Objectif

Produire un rapport d'analyse listant les modèles, services, repositories, contrôleurs et utilitaires existants à réutiliser avant de développer le workflow d'import de collection utilisateur.

Le livrable attendu est un fichier Markdown :

`tasks/user_collection/01_existing_code_analysis_result.md`

## Étapes

1. Lire `tasks/user_collection/user_collection_workflow.md`.
2. Lire les documentations concernées :
   - `documentation/database.md`
   - `documentation/authentication.md`
   - `documentation/site-plan.md`
   - `documentation/backend-arch.md`
   - `documentation/frontend-arch.md`
3. Identifier les modèles backend existants :
   - utilisateur
   - jeu
   - plateforme
   - studio
   - association collection utilisateur
4. Identifier les repositories ou services existants pour :
   - utilisateurs
   - jeux
   - plateformes
   - studios
   - collections utilisateur
5. Identifier le code existant qui lit déjà les fichiers ODS.
6. Identifier les conventions actuelles pour :
   - contrôleurs backend
   - services backend
   - tests backend
   - appels API frontend
   - pages ou features frontend
7. Créer le fichier `tasks/user_collection/01_existing_code_analysis_result.md`.
8. Dans ce fichier, documenter :
   - les fichiers existants à réutiliser
   - les fichiers existants à modifier
   - les nouveaux fichiers probablement nécessaires
   - les modèles et champs concernés
   - les services ou repositories concernés
   - le lecteur ODS existant à factoriser
   - les tests existants à compléter
   - les risques ou ambiguïtés détectés

## Critères d'acceptation

- Le fichier `tasks/user_collection/01_existing_code_analysis_result.md` existe.
- Les fichiers existants à modifier ou réutiliser y sont listés.
- Les modèles et champs réels de la base y sont confirmés, notamment `developer` ou `developper`.
- Le lecteur ODS existant à factoriser y est identifié.
- Les conventions de test à suivre y sont identifiées.
- Les risques techniques et points d'attention y sont listés.

## Validation attendue

- Aucun changement fonctionnel.
- Aucun test obligatoire sauf si le projet impose une validation après toute modification documentaire.
- Relire le rapport produit avant de démarrer la tâche 02.
