Le but de la tache est de vérifier les valeurs retourner le reader lors de l'import pour s'assurer que les valeurs retournés sont du bon type pour chaque colonne de la table t_games a crééer.
Le but est de s'assurer que lors du mapping l'utilisateur n'a pas fait une erreur de mappging.
- Nom : Doit etre une String et ne peux pas être une date
- Studio : Doit etre une String et ne peux pas être une date
- Plateforme : Doit etre une String et ne peux pas être une date
- release  date : Doit etre une date Valide entre "1970 et 2100"
- date d'achat : Doit etre une date Valide entre "1970 et 2100"

Dans le cas contraire un log d'erreur coté backend est levée et l'import est annulé complétement. Une erreur claire et précise est remonté au frontend indiquant a l'utilisateur l'erreur de mapping précise.