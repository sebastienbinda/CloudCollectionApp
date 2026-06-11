# Blocage des imports pendant reset

## Objectif

Empêcher les utilisateurs de lancer ou poursuivre un workflow d'import pendant
qu'un reset Bibliotheque est en cours.

## Périmètre

- Utiliser le coordinateur de reset créé dans la sous-tâche `01`.
- Retourner `403 Forbidden` quand un reset est en cours sur les endpoints liés à
  l'import utilisateur.
- Endpoints concernés :
  - upload du fichier d'import ;
  - analyse du fichier ;
  - import final ;
  - récupération de configuration d'import ;
  - réinitialisation de collection utilisateur.
- Retourner un message JSON clair, par exemple :

```json
{
  "error": "Un reset de la Bibliotheque est en cours. Veuillez réessayer plus tard."
}
```

- Ne pas modifier les comportements existants lorsque aucun reset n'est en
  cours.

## Tests attendus

- Chaque endpoint concerné retourne `403` pendant un reset.
- Chaque endpoint garde son comportement existant hors reset.
- Le message d'erreur ne révèle aucun détail interne.

## Critères d'acceptation

- Le blocage est centralisé autant que possible.
- Les règles d'authentification existantes des endpoints restent inchangées.
