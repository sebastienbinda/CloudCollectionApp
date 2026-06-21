Ajout des informations privées sur les jeux de la collection des utilsiateurs : 
 - Prix d'achat : Long
 - Lieu d'achat : String
 - Date d'achat : Date
 - Note : String
 - Etat : Enuméré [Mauvais,Correct,Bon,Très bon,Neuf], en bd on écrit un entier le mapping vers une string est fait au niveau frontend uniquement.
 - Notice : boolean
 - Collector : boolean
 - Steelbook : boolean
 - Digital version : boolean
 - Region : Choix parmis la liste des pays (enuméré): 
     - JAP
     - US
     - EU-FR
     - EU-UK
     - EU-DE
     - EU-ES
     - EU-IT
     - AU
     - ASIA
     - KOR
     - TWN
     - HK
     - CHN
 - Description

Ces informations doivent être ajoutées dans la table t_user_collection.

Lors de l'import, il faut aussi demander la colonne associée aux nouvelles informations. Ces informations sont optionelles. leur valeur peut etre null.
Dans ce cas, on affiche pas l'information dans l'écran de détail du jeu de la collection. Si les informations sont bien présentes elles doivent apparaître dans l'écran de detail d'un jeu. La Region est affichée avec un drapeau représentant la region.

Il faut rajouter une notion de unité de prix lorsque l'utilisateur importe son fichier. Ce  doit etre dans la conf d'import et etre ajouté a la table t_user_collection : avec une nouvelle colonne price_unit de type euros, dollars,...
Dans l'écran d'import cette information est préremplie en fonction de la local du navigateur.
 
Lors de l'import, il faut utiliser les memes algo que pour detcter les plateformes pour trouver la bonne valeur de l'enuméré des regions, si le score est inférieur a une valeur configurable via env (REGION_MATCH_LIMIT) avec 60 par défaut. Si le score est inférieur, le jeu n'est pas rejeté mais un warning apparait dans le rapport et a l'ihm et la valeur est laissé vide en base

Lors de l'import, il faut utiliser les memes algo que pour detcter l'état pour trouver la bonne valeur de l'enuméré des etats, si le score est inférieur a une valeur configurable via env (ETAT_MATCH_LIMIT) avec 60 par défaut. il faut que l'algo prenne aussi en compte les mots en anglais qui peuvent matché l'état. Dans le fichier d'import, la valeur doit etre une string qu'il faut matcher sur l'énuméré possible. Si le score est inférieur, le jeu n'est pas rejeté mais un warning apparait dans le rapport et a l'ihm et la valeur est laissé vide en base

Pour les 4 colonnes boolean,  il faut également trouver le boolean qui correspond a la chaine avec toutes les valeurs possible pour ce genre de colonne type Oui, Non,  Yes, No, X, vide, fait moi une proposition avant d'implémenter. Si la valeur ne match pat, le jeu n'est pas rejeté mais un warning apparait dans le rapport et a l'ihm et la valeur est laissé vide en base

 Pour le prix d'achat, il faut vérifier que le prix n'est pas négatif.