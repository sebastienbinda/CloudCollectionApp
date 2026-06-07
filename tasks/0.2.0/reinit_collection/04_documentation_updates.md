# 04 - Documentation fonctionnelle

## Objectif

Mettre à jour la documentation concernée par le nouveau workflow de
réinitialisation de collection.

Cette tâche dépend de :

- `01_backend_reinit_contract.md`
- `02_backend_reinit_service_and_persistence.md`
- `03_frontend_configuration_reinit_action.md`

## Documents À Vérifier

Vérifier et mettre à jour si nécessaire :

- `documentation/backend-api.md`
- `documentation/import.md`
- `documentation/site-plan.md`
- `documentation/frontend-arch.md`
- `documentation/backend-arch.md`
- `documentation/database.md`
- `README.md`

## Contenu Minimal Attendu

Documenter :

- le endpoint `POST /api/users/collection/reinit` ;
- les codes `200`, `404` et `500` ;
- le fait que l'utilisateur est dérivé du token ;
- le nettoyage de `t_user_collection` ;
- le nettoyage de `t_user.collection_file_path` et
  `t_user.collection_file_description` ;
- le comportement lorsque le fichier disque est absent ;
- la redirection frontend vers `/collection/import` après succès.

## Gouvernance

Si une règle existante de documentation est contredite ou affaiblie, demander
confirmation avant modification.

Si la fonctionnalité crée un bloc fonctionnel jugé autonome, proposer la
création d'une documentation dédiée et attendre confirmation avant de la créer.

## Contraintes

- Ne pas documenter de comportement qui n'est pas implémenté.
- Ne pas exposer de chemin local spécifique à un développeur.
- Mettre à jour `README.md` seulement si le comportement utilisateur, les routes
  ou les commandes visibles changent.
