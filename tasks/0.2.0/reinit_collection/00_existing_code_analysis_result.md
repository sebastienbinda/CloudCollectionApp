# 00 - Rapport d'analyse existante et contrat fonctionnel

## Synthèse

La tâche peut être implémentée sans nouveau framework, sans migration Alembic et
sans changement de schéma. Elle touche un workflow déjà existant : la collection
utilisateur est considérée comme importée par `t_user.collection_file_path`, et
le frontend sait déjà rediriger un utilisateur `USER` sans collection vers
`/collection/import` via `GET /api/users/me/collection`.

Le point d'intégration le plus naturel côté backend est le contrôleur
`UserCollectionImportController`, car il possède déjà :

- les routes self-service utilisateur sous `/api/users/**` ;
- la résolution de l'utilisateur connecté depuis le Bearer token ;
- l'injection du repository transactionnel d'import ;
- le mapping des erreurs d'import et de statut collection.

Côté frontend, l'action doit rester dans la page Configuration, l'appel HTTP
doit être ajouté au service `UserCollectionApi.js` et l'orchestration doit être
placée dans un nouveau hook dédié à la réinitialisation, afin de respecter
l'architecture React existante.

## Contrat Confirmé

- Endpoint cible : `POST /api/users/collection/reinit`.
- Autorisation : endpoint protégé avec profil minimum `USER`.
- Utilisateur cible : toujours dérivé du Bearer token, jamais depuis le body,
  l'URL ou une query string.
- Succès `200` :

```json
{
  "reinitialized": true
}
```

- Absence de collection `404` :

```json
{
  "error": "Collection introuvable."
}
```

- Erreur inattendue `500` :

```json
{
  "error": "Unable to reinitialize collection."
}
```

- Le `404` s'applique uniquement quand `collection_file_path` est `NULL` et
  qu'il n'existe aucune entrée dans `t_user_collection` pour l'utilisateur.
- Si `collection_file_path` pointe vers un fichier absent sur disque, la
  réinitialisation continue et un warning est journalisé.
- Si une suppression disque échoue pour une autre raison, le endpoint retourne
  `500` et les modifications SQL doivent être rollbackées.

## Fichiers À Modifier

Backend :

- `backend/controllers/user_collection_import_controller.py`
- `backend/services/users/user_collection_import_service.py`
- `backend/services/database/user_collection_import_repository.py`
- `backend/services/database/user_collection_file_repository.py`
- `backend/services/database/user_collection_repository.py`
- `backend/services/database/__init__.py` si de nouvelles classes publiques sont
  exportées
- `backend/tests/test_user_collection_routes.py`
- `backend/tests/test_user_collection_import_service.py`
- `backend/tests/test_user_collection_file_repository.py`
- `backend/tests/test_user_collection_repository.py`
- `backend/tests/route_test_support.py`

Frontend :

- `frontend/src/services/UserCollectionApi.js`
- `frontend/src/hooks/app/useCloudCollectionViewModel.js`
- nouveau hook dédié dans `frontend/src/hooks/collection/`, par exemple
  `useUserCollectionReinitialization.js`
- `frontend/src/hooks/collection/useUserCollectionOnboarding.js` seulement pour
  réutiliser son mécanisme de contrôle ou de redirection si nécessaire
- `frontend/src/components/AppViewSwitch.jsx`
- `frontend/src/components/ConfigurationView.jsx`
- `frontend/src/services/BackendRouteAccessService.js` si la visibilité de
  l'action doit dépendre du catalogue `/api/routes`

Documentation :

- `documentation/backend-api.md`
- `documentation/import.md`
- `documentation/site-plan.md`
- `documentation/frontend-arch.md`
- `documentation/backend-arch.md`
- `documentation/authentication.md`
- `README.md` si le nouveau comportement utilisateur ou la nouvelle route doit
  être exposé aux mainteneurs.

## Classes Et Hooks À Étendre

Backend :

- `UserCollectionImportController` : ajouter la route, résoudre l'utilisateur
  courant et mapper les erreurs métier vers `200`, `404` et `500`.
- `UserCollectionImportService` : ajouter l'orchestration de réinitialisation
  en réutilisant le service d'import existant, sans créer de nouveau service
  backend dédié.
- `SqlAlchemyUserCollectionImportRepository` : ajouter une opération
  transactionnelle de réinitialisation en réutilisant le repository d'import
  existant.
- `SqlAlchemyUserCollectionFileRepository` : ajouter une lecture verrouillée du
  chemin collection et une remise à `NULL` de `collection_file_path` et
  `collection_file_description`.
- `SqlAlchemyUserCollectionRepository` : ajouter un comptage et une suppression
  des lignes `t_user_collection` par `user_id`.

Frontend :

- `UserCollectionApi` : ajouter `reinitializeCollection()` avec
  `BackendAvailabilityGuard.fetch` et les headers Bearer existants.
- Nouveau hook dédié, par exemple `useUserCollectionReinitialization` : porter
  l'état `isReinitializingCollection`, l'erreur de réinitialisation et l'action
  confirmée.
- `useCloudCollectionViewModel` : exposer l'action et ses états à
  `AppViewSwitch`.
- `AppViewSwitch` : transmettre les props à `ConfigurationView`.
- `ConfigurationView` : afficher la carte d'action, demander confirmation et
  déclencher le callback.
- `BackendRouteAccessService` : ajouter un drapeau, par exemple
  `canReinitializeCollection`, si l'action doit être activée seulement quand le
  catalogue backend expose la route.

## Points De Réutilisation Existants

- `UserCollectionImportController._current_user_id()` résout déjà le `user_id`
  depuis `payload.sub`.
- `AuthGuard.require_profile(UserProfile.USER.value)` protège déjà les routes
  self-service de collection.
- `SqlAlchemyUserCollectionFileRepository.user_has_collection()` lit déjà
  `collection_file_path`.
- `UserCollectionImportService` centralise déjà l'orchestration métier du
  workflow d'import utilisateur et doit aussi porter la réinitialisation.
- `SqlAlchemyUserCollectionImportRepository` centralise déjà la transaction SQL
  du workflow d'import utilisateur et doit aussi porter la transaction de
  réinitialisation.
- `SqlAlchemyUserRepository.delete_user()` montre déjà la requête de suppression
  des lignes `t_user_collection` d'un utilisateur.
- `useUserCollectionOnboarding.openOnboardingWhenCollectionIsMissing()` sait
  ouvrir l'onboarding après lecture du statut.
- `UserCollectionApi.fetchJson()` centralise déjà parsing JSON, erreurs typées,
  session expirée et disponibilité backend.

## Tests Backend À Ajouter Ou Modifier

Tests de route dans `backend/tests/test_user_collection_routes.py` :

- `POST /api/users/collection/reinit` sans token retourne l'erreur
  d'authentification existante ;
- succès `200` avec `{"reinitialized": true}` ;
- `404` quand `collection_file_path` est absent et aucune ligne collection
  n'existe ;
- `500` quand le service lève une erreur inattendue ;
- l'appel service reçoit l'identifiant utilisateur `7`, résolu depuis le token
  de test.

Tests service :

- réinitialisation nominale supprime les associations, nettoie les champs user
  et supprime le fichier ;
- fichier absent accepté avec warning ;
- erreur disque autre que fichier absent remonte une erreur métier ;
- absence de collection selon la règle `collection_file_path IS NULL` et aucune
  ligne dans `t_user_collection` ;
- présence de lignes `t_user_collection` sans chemin fichier déclenche une
  réinitialisation, pas un `404`.

Tests repository :

- comptage des lignes `t_user_collection` par utilisateur ;
- suppression des lignes `t_user_collection` par utilisateur ;
- remise à `NULL` de `collection_file_path` et
  `collection_file_description` ;
- verrouillage ou lecture transactionnelle du user avant réinitialisation.

## Validations Frontend À Lancer

- `cd frontend && npm run build`
- Vérification manuelle de `/configuration` en profil `USER` :
  - carte `Réinitialiser la collection` visible ;
  - annulation de confirmation sans appel backend ;
  - confirmation avec succès redirige vers `/collection/import`.
- Vérification manuelle en profil `ADMIN` :
  - action absente ;
  - les règles existantes de redirection admin vers `/configuration` restent
    intactes.
- Vérification des erreurs :
  - `404` affiche une erreur lisible ;
  - `401` ou `403` déclenche le comportement de session expirée existant ;
  - `500` affiche une erreur générique.

## Documentations Concernées

- `documentation/backend-api.md` : ajouter le endpoint, l'autorisation et les
  réponses.
- `documentation/import.md` : documenter que la réinitialisation permet un
  nouvel import après nettoyage de la collection courante.
- `documentation/site-plan.md` : confirmer que le succès renvoie vers
  `/collection/import`.
- `documentation/frontend-arch.md` : préciser l'action de Configuration si la
  documentation des hooks collection est étendue avec le nouveau hook dédié.
- `documentation/backend-arch.md` : confirmer le placement controller, service
  et repository.
- `documentation/authentication.md` : ajouter la route dans la liste des routes
  connectées utilisateur.
- `documentation/database.md` : vérifier seulement ; pas de changement de
  structure attendu.
- `README.md` : vérifier après implémentation si la route ou le comportement
  utilisateur doivent être mentionnés.

## Risques Et Décisions Techniques

- La transaction SQL ne peut pas rollbacker une suppression fichier déjà faite.
  Pour respecter au mieux le contrat, le service doit effectuer la suppression
  fichier dans le bloc de workflow avant validation définitive de la transaction
  SQL, et remonter toute erreur disque non acceptable avant commit.
- Le fichier absent doit être traité explicitement avec `Path.unlink()` ou une
  vérification préalable afin de journaliser un warning, car `missing_ok=True`
  seul ne permet pas de signaler clairement l'anomalie.
- Comme `ADMIN` hérite des droits backend `USER`, la route backend sera
  techniquement accessible à `ADMIN` si elle utilise le profil minimum `USER`.
  Le frontend doit continuer à masquer les écrans et actions de propriété de
  collection pour `ADMIN`.
- Le `404` dépend de deux sources (`collection_file_path` et
  `t_user_collection`). Le repository doit éviter deux lectures non verrouillées
  séparées qui pourraient créer un état incohérent pendant une opération
  concurrente.

## Conclusion

La suite peut commencer par la sous-tâche `01_backend_reinit_contract.md`.
L'implémentation doit rester incrémentale : route et mapping d'erreurs d'abord,
extension du service et du repository d'import existants, puis nouveau hook
frontend dédié, intégration Configuration et documentation.
