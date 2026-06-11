# Factorisation du coeur d'import backend

## Objectif

Centraliser les étapes communes d'import de collection afin que l'import
utilisateur classique et le reset Bibliotheque utilisent exactement le même
coeur d'exécution.

## Constat

Le reset réutilise déjà les composants principaux de l'import utilisateur :

- `CollectionFileReaderFactory` ;
- les lecteurs de fichiers ;
- `CollectionImportDateValidator` ;
- `SqlAlchemyUserCollectionImportRepository.import_collection(...)` ;
- le mapping `UserCollectionImportResult`.

Cependant, les étapes `validation fichier -> lecture -> validation dates ->
persistance -> mapping résultat -> mapping erreurs` sont encore orchestrées à
deux endroits :

- dans `UserCollectionImportService._import_collection_locked(...)` pour
  l'import utilisateur ;
- dans `StoredUserCollectionImportService._import_stored_collection_locked(...)`
  pour le reset Bibliotheque.

## Périmètre

- Extraire dans `UserCollectionImportService` une méthode centralisée réalisant
  toutes les étapes métier communes de l'import :
  - validation de la description d'import ;
  - création du reader ;
  - validation du fichier source ;
  - lecture du fichier ;
  - validation des dates ;
  - appel transactionnel au repository ;
  - conversion en `UserCollectionImportResult` ;
  - conversion des erreurs fonctionnelles et inattendues.
- Permettre à cette méthode centralisée de gérer les deux modes :
  - import utilisateur avec copie préalable du fichier vers le workspace ;
  - import reset depuis un fichier déjà stocké, sans nouvelle copie.
- Garder dans les méthodes publiques uniquement les responsabilités spécifiques :
  - upload/analyse temporaire ;
  - choix du chemin source ou cible ;
  - suppression du fichier copié en cas d'échec ou après import temporaire ;
  - verrou utilisateur.
- Modifier `StoredUserCollectionImportService` pour déléguer au coeur centralisé
  au lieu de réimplémenter lecture/persistance/mapping.
- Ne pas changer le contrat HTTP ni le comportement fonctionnel existant.

## Hors périmètre

- Changement de schéma base.
- Changement du endpoint `POST /api/library/reset`.
- Changement frontend.
- Changement du format des rapports email.

## Tests attendus

- Les tests existants de `UserCollectionImportService` restent verts.
- Les tests existants de `StoredUserCollectionImportService` restent verts.
- Ajouter ou modifier un test prouvant que le reset et l'import utilisateur
  passent par le même coeur d'import centralisé.
- Vérifier que l'import utilisateur copie toujours le fichier dans le workspace.
- Vérifier que l'import reset ne copie pas le fichier déjà stocké.
- Vérifier que les erreurs de lecture, validation et persistance gardent les
  mêmes exceptions fonctionnelles qu'avant.

## Critères d'acceptation

- Une seule méthode porte la séquence métier commune de l'import.
- `StoredUserCollectionImportService` ne duplique plus les étapes de lecture,
  validation dates, persistance et mapping résultat.
- Le reset Bibliotheque et l'import utilisateur divergent uniquement sur la
  préparation du fichier source/cible et le nettoyage de fichier.
- Aucun comportement utilisateur ou API existant n'est modifié.
- Les tests backend passent.
