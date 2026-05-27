# 02 bis - Index SQL de consultation collection utilisateur

## Objectif

Ajouter les index SQL utiles aux nouvelles requêtes de consultation de
collection utilisateur afin de limiter les temps de réponse lorsque les tables
`t_user_collection` et `t_game` grandissent.

Cette tâche doit s'appuyer sur :

- `tasks/user_collection_view/00_existing_code_analysis_result.md`
- `tasks/user_collection_view/02_backend_sql_collection_read_model.md`
- les requêtes créées pour la consultation SQL utilisateur.

## Constat

Les contraintes existantes créent déjà des index implicites utiles :

- `t_user_collection(user_id, game_id)` via la clé primaire ;
- `t_game(id)` via la clé primaire ;
- `t_game(name, platform)` via la contrainte unique ;
- `t_platform(id)` via la clé primaire ;
- `t_studio(id)` via la clé primaire ;
- `t_studio(name)` via la contrainte unique.

Les nouvelles requêtes partent principalement de `t_user_collection.user_id`,
puis joignent `t_game`, `t_platform` et `t_studio`. La clé primaire de
`t_user_collection` couvre déjà efficacement le filtre principal par
utilisateur.

## Index à créer

Créer une nouvelle migration Alembic qui ajoute les index suivants :

```sql
CREATE INDEX ix_t_user_collection_game_id
ON <schema>.t_user_collection (game_id);
```

Utilité :

- accélérer les futures requêtes partant d'un jeu vers les collections ;
- améliorer les opérations liées à la clé étrangère `game_id` ;
- préparer les évolutions de suppression ou diagnostic par jeu.

```sql
CREATE INDEX ix_t_game_platform
ON <schema>.t_game (platform);
```

Utilité :

- optimiser les jointures `t_game.platform = t_platform.id` ;
- optimiser les listes, regroupements et filtres par plateforme.

```sql
CREATE INDEX ix_t_game_developer
ON <schema>.t_game (developer);
```

Utilité :

- optimiser les jointures `t_game.developer = t_studio.id` ;
- préparer les filtres et tris par studio.

## Points explicitement exclus

Ne pas ajouter d'index `btree` simple sur les colonnes texte `name` pour les
recherches `contains`, car les requêtes utilisent une expression du type :

```sql
TRANSLATE(LOWER(column), ...) LIKE '%texte%'
```

Un index `btree` classique ne serait pas efficace pour ce contrat.

Ne pas ajouter l'extension PostgreSQL `pg_trgm` dans cette tâche. Les index GIN
sur expression normalisée peuvent être envisagés plus tard, après mesure avec
`EXPLAIN ANALYZE` et confirmation explicite, car cela introduit une extension
PostgreSQL supplémentaire.

## Étapes

1. Vérifier les index déjà créés par les clés primaires et contraintes uniques.
2. Créer une nouvelle migration Alembic forward-only.
3. Ajouter les index avec des noms explicites :
   - `ix_t_user_collection_game_id`
   - `ix_t_game_platform`
   - `ix_t_game_developer`
4. Utiliser le schema configuré par Alembic, comme les migrations existantes.
5. Ajouter le `downgrade` correspondant pour supprimer uniquement ces index.
6. Mettre à jour `documentation/database.md` pour documenter les index.
7. Ajouter ou mettre à jour les tests backend de migration ou de schéma si le
   projet dispose déjà d'un test adapté.
8. Vérifier que les repositories de consultation n'ont pas besoin de changement
   fonctionnel.

## Critères d'acceptation

- Les trois index sont créés par une migration Alembic dédiée.
- Les noms d'index sont explicites et stables.
- La migration respecte le schema PostgreSQL configuré.
- La migration ne modifie pas les tables, colonnes, contraintes ou données
  existantes.
- `documentation/database.md` liste les nouveaux index.
- Aucun nouveau framework ou dépendance n'est ajouté.
- Aucun secret ou chemin local n'est introduit.

## Validation attendue

- Lancer les tests backend :

```bash
./test_backend.sh
```

- Vérifier le format du diff :

```bash
git diff --check
```

- Si une base locale avec données réalistes est disponible, comparer les plans
  d'exécution avant/après avec :

```sql
EXPLAIN ANALYZE
```

sur les requêtes principales :

- statistiques globales de collection ;
- liste des plateformes utilisateur ;
- liste des jeux utilisateur filtrée par `platform_id` ;
- liste des jeux utilisateur filtrée par `studio_name`.

## Documentation concernée

- `documentation/database.md` : concerné, à mettre à jour.
- `documentation/backend-arch.md` : non concerné sauf si la stratégie de
  migration change.
- `documentation/backend-api.md` : non concerné, aucun contrat HTTP ne change.
- `README.md` : à vérifier, mais probablement non concerné car le comportement
  utilisateur et les commandes ne changent pas.
