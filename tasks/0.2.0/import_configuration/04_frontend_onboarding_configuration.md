# 04 - Onboarding frontend de configuration d'import

## Objectif

Adapter la page d'onboarding pour collecter la configuration d'import et
l'envoyer avec le fichier dans `POST /api/users/import`.

Cette tâche dépend de :

- `01_import_configuration_contract.md`
- `03_backend_import_endpoint_and_persistence.md`

## Parcours Utilisateur

La page d'onboarding demande :

1. Type de fichier : LibreOffice, seul choix disponible pour l'instant.
2. Multiple onglets : Oui ou Non.
3. Si multiple onglets :
   - information portée par l'onglet : Plateforme pour le périmètre UI initial ;
   - mêmes plages de données sur chaque onglet : Oui ou Non.
4. Si mêmes plages :
   - onglets inclus optionnels ;
   - plage de données ;
   - ligne d'en-tête ;
   - colonnes des champs nécessaires.
5. Si plages différentes :
   - configuration par onglet ;
   - `sheet_name` ;
   - plage de données ;
   - ligne d'en-tête ;
   - colonnes des champs nécessaires.
6. Si pas de multiple onglets :
   - plage de données ;
   - ligne d'en-tête ;
   - colonnes des champs nécessaires, dont `platform`.

## Configuration À Envoyer

Construire un JSON conforme à `01_import_configuration_contract.md` et l'envoyer
dans le champ multipart texte `collection_file_description`.

Le fichier reste envoyé dans `collection_file`.

Ne pas définir manuellement le header `Content-Type` côté frontend lorsque
`FormData` est utilisé.

## Responsabilités Frontend

- Le frontend collecte les choix utilisateur.
- Le frontend peut faire des validations UX simples : champs requis,
  valeur vide, format de base.
- Le backend reste responsable de la validation contractuelle complète.
- Les appels HTTP restent dans `frontend/src/services/`.
- L'orchestration reste dans `frontend/src/hooks/collection/`.

## Tests Et Validation

Mettre à jour ou ajouter les validations nécessaires pour :

- envoyer `collection_file` et `collection_file_description` dans le même
  `FormData` ;
- construire le JSON `single_sheet_conf` ;
- construire le JSON `multiple_sheets_conf.shared_layout` ;
- construire le JSON `multiple_sheets_conf.sheets` ;
- afficher les erreurs backend `422` de façon compréhensible.

Lancer :

```bash
cd frontend
npm run build
```

## Critères D'Acceptation

- L'utilisateur peut configurer les trois modes prévus.
- Le payload multipart respecte le contrat backend.
- Les erreurs `422` sont affichées.
- Le build frontend passe.
