# Orchestration backend du reset et des imports

## Objectif

Implémenter le traitement asynchrone qui vide la Bibliotheque puis reconstruit
les données à partir des fichiers et configurations d'import utilisateurs.

## Périmètre

- Supprimer en base les données de :
  - `t_user_collection` ;
  - `t_game` ;
  - `t_platform` ;
  - `t_studio`.
- Respecter les contraintes de clés étrangères et l'ordre de suppression
  identifié dans l'analyse.
- En cas d'échec du clean base, arrêter le reset, enregistrer l'erreur dans le
  contexte mémoire et rollback les changements base déjà réalisés.
- Charger les utilisateurs ayant un `collection_file_path` renseigné, ordonnés
  par date d'enregistrement.
- Pour chaque utilisateur :
  - ignorer et journaliser le cas fichier absent ou illisible ;
  - ignorer et journaliser le cas `collection_file_description` null ou vide ;
  - réutiliser le service d'import existant ;
  - passer à l'utilisateur suivant en cas d'échec d'import ;
  - enregistrer succès et erreurs dans le contexte mémoire du job.
- Accepter qu'un ou plusieurs échecs utilisateurs produisent une Bibliotheque
  reconstruite partiellement avec les imports réussis.
- Envoyer en fin de job un email à l'adresse administrateur configurée par
  variable d'environnement, avec le résultat global et le contexte succès/erreur.

## Hors périmètre

- Le blocage des endpoints d'import pendant reset.
- Les changements frontend.
- Un endpoint de statut.

## Tests attendus

- Clean base réalisé dans le bon ordre.
- Rollback si le clean base échoue.
- Les utilisateurs sont traités dans l'ordre attendu.
- Fichier manquant ou illisible : erreur enregistrée et utilisateur suivant.
- Configuration absente : erreur enregistrée et utilisateur suivant.
- Échec d'import utilisateur : erreur enregistrée et utilisateur suivant.
- Succès partiel accepté et reporté dans le contexte.
- Email final envoyé avec succès et erreurs.

## Critères d'acceptation

- Le service d'import existant est réutilisé, sans dupliquer les règles métier
  d'import.
- Un échec utilisateur ne bloque pas les autres imports.
- Un échec de clean base bloque le reset et rollback la base.
