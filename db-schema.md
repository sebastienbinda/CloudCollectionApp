TABLE t_plateform
 - id : big int not null
 - name : Varchar2(64) not null
 - release_date : Datetime 
 - manufacturer : Varchar2(128)
 - description : jsonb
 - status : Varchar2(16) not null
Primary Key : id

SEQUENCE s_platforme
 - t_platform->id

t_game
 - id : big int not null
 - name : Varchar2(256) not null
 - release_date : Datetime 
 - developper : clef étrangere t_studio->id
 - editor : clef étrangere t_studio->id
 - platform : clef étrangere t_platform->id not null
 - description : jsonb
Primary Key : id
Unique Key : name/platform

SEQUENCE s_game
 - t_game->id

t_studio
 - id : big int not null
 - name : Varchar2(256) not null
 - country : Varchar2(256)
 - city : Varchar2(256)
 - creation_date : Datetime
 - status : Varchar2(16) not null

SEQUENCE s_studio
 - t_studio->id

t_user
 - id : big int
 - email : Varchar2(256) not null
 - password_encrypter : Varchar2(512) not null
 - creation_date : Datetime not null
 - last_connexion_date : Datetime 
 - collection_file_path : Varchar2(512) 
 - collection_file_description : Jsonb

SEQUENCE s_user
 - t_user->id

t_user_collection
 - user_id : big int
 - game_id : big_int
 - game_additional_name : Varchar2(256)
 - collection_file_location : 