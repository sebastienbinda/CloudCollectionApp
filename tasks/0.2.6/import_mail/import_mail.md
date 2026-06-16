Aujourd'hui le mail d'import est envoyé a l'admin en cas d'erreur ou warning, je veux que le mail soit toujours envoyé avec toutes les informations du context d'import. Il faut bien centraliser l'envoi du mail en dehors du reader et ne pas dépendre. du type de fichier. et l'envoie est fait en toute fin d'import. On envoie un seul mail par import.

## Résultat Branche `menu_highlight` - 2026-06-16

La tâche est réalisée.

Changements appliqués :

- ajout d'un contexte de rapport d'import utilisateur avec l'utilisateur, le type
  de fichier, le nom du fichier, le mode source, les compteurs, les warnings et
  la configuration validée ;
- ajout d'un notifier administrateur dédié à l'import utilisateur ;
- envoi d'un seul rapport à la toute fin de l'import, après lecture, validation,
  matching, persistance et calcul de durée ;
- envoi du rapport même quand l'import ne contient aucun warning ;
- centralisation hors reader : le reader ne déclenche aucun email et le notifier
  ne dépend pas du type de fichier ;
- protection de l'import réussi contre un échec d'envoi email : l'erreur est
  journalisée sans transformer l'import en erreur fonctionnelle.

Validations :

- tests unitaires du service d'import utilisateur mis à jour ;
- tests unitaires du notifier administrateur ajoutés ;
- documentation `documentation/import.md` et `documentation/backend-api.md`
  mise à jour.
