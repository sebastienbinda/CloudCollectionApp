Lors de l'affichage des jeux dans la vue bibliotheque le sereur retourne une erreur 500 : 
Unable to read library games: (psycopg.DataError) timestamp too large (after year 10K): '48113-11-21 00:00:01' (Background on this error at: https://sqlalche.me/e/20/9h9h)

L'import doit vérifier la validité des dates avant l'insertion en base de données. Non pas dans le reader car il peut etre abstrait en fonction du type de fichier mais au niveau supérieur du service.