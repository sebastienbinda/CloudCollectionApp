# 03 - Action frontend dans Configuration

## Objectif

Ajouter l'action `Réinitialiser la collection` dans la page Configuration pour
les utilisateurs `USER` possédant les vues de collection.

Cette tâche dépend de :

- `01_backend_reinit_contract.md`
- `02_backend_reinit_service_and_persistence.md`

## Emplacement

Modifier la page :

- `frontend/src/components/ConfigurationView.jsx`

Respecter l'architecture existante :

- appel HTTP dans `frontend/src/services/UserCollectionApi.js` ou service
  équivalent existant ;
- orchestration dans un nouveau hook dédié sous
  `frontend/src/hooks/collection/`, par exemple
  `useUserCollectionReinitialization.js` ;
- composant centré sur l'affichage et les interactions utilisateur.

## Interface

Dans la page Configuration, ajouter une section qui :

- explique que l'action supprime la collection actuelle pour permettre un nouvel
  import ;
- explique que le fichier de collection est aussi supprimé du serveur ;
- demande confirmation avant l'appel backend ;
- affiche un état de chargement pendant l'appel ;
- affiche une erreur lisible si l'appel échoue.

## Appel Backend

Appeler :

```http
POST /api/users/collection/reinit
```

avec les headers d'authentification existants et le
`BackendAvailabilityGuard`.

## Navigation Après Succès

Après succès :

- rafraîchir les signaux de collection nécessaires ;
- réutiliser le mécanisme existant de statut collection si possible ;
- rediriger vers `/collection/import` car l'utilisateur n'a plus de collection.

## Contraintes Frontend

- Créer un hook dédié à la réinitialisation, séparé du hook d'onboarding
  d'import.
- Ne pas afficher l'action au profil `ADMIN`.
- Ne pas dupliquer les règles métier backend côté frontend.
- Ne pas recréer de header, menu ou footer.
- Garder la page dans `PageLayout`.
- Ne pas ajouter de dépendance frontend.

## Validation Frontend

Vérifier :

- l'action est visible pour un `USER` authentifié ;
- l'action est absente pour `ADMIN` ;
- la confirmation bloque l'appel si l'utilisateur annule ;
- le succès ouvre l'onboarding d'import ;
- les erreurs `404`, `401/403` et `500` sont affichées proprement.
