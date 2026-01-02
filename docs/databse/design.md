# db

```
games
  - id (integer, not null, primary key, unique)
  - name
  - description
  - minplayers
  - maxplayers

pieces
  - id (integer, not null, primary key, unique)
  - name
  - game_id-it_belongs_to

player
  - id (integer, not null, primary key, unique)
  - name
  - ...

API_URL: http....
WOPR_VERSION: ....
STORAGE_DIR: /.....
```


Add/edit/remove games
Add/edit/remove pieces
Add/edit/remove mlimages



```
wopr-db=> \d games
                                           Table "public.games"
    Column     |              Type              | Collation | Nullable |              Default              
---------------+--------------------------------+-----------+----------+-----------------------------------
 id            | integer                        |           | not null | nextval('games_id_seq'::regclass)
 document_id   | character varying(255)         |           |          | 
 uid           | character varying(255)         |           |          | 
 name          | character varying(255)         |           |          | 
 description   | text                           |           |          | 
 min_players   | integer                        |           |          | 
 max_players   | integer                        |           |          | 
 create_time   | timestamp(6) without time zone |           |          | 
 update_time   | timestamp(6) without time zone |           |          | 
 created_at    | timestamp(6) without time zone |           |          | 
 updated_at    | timestamp(6) without time zone |           |          | 
 published_at  | timestamp(6) without time zone |           |          | 
 created_by_id | integer                        |           |          | 
 updated_by_id | integer                        |           |          | 
 locale        | character varying(255)         |           |          | 
Indexes:
    "games_pkey" PRIMARY KEY, btree (id)
    "games_created_by_id_fk" btree (created_by_id)
    "games_documents_idx" btree (document_id, locale, published_at)
    "games_updated_by_id_fk" btree (updated_by_id)
Foreign-key constraints:
    "games_created_by_id_fk" FOREIGN KEY (created_by_id) REFERENCES admin_users(id) ON DELETE SET NULL
    "games_updated_by_id_fk" FOREIGN KEY (updated_by_id) REFERENCES admin_users(id) ON DELETE SET NULL
Referenced by:
    TABLE "ml_image_metadatas_game_lnk" CONSTRAINT "ml_image_metadatas_game_lnk_ifk" FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
    TABLE "pieces_game_lnk" CONSTRAINT "pieces_game_lnk_ifk" FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE

wopr-db=> \d pieces
                                           Table "public.pieces"
    Column     |              Type              | Collation | Nullable |              Default               
---------------+--------------------------------+-----------+----------+------------------------------------
 id            | integer                        |           | not null | nextval('pieces_id_seq'::regclass)
 document_id   | character varying(255)         |           |          | 
 name          | character varying(255)         |           |          | 
 uid           | character varying(255)         |           |          | 
 create_time   | timestamp(6) without time zone |           |          | 
 update_time   | timestamp(6) without time zone |           |          | 
 description   | text                           |           |          | 
 created_at    | timestamp(6) without time zone |           |          | 
 updated_at    | timestamp(6) without time zone |           |          | 
 published_at  | timestamp(6) without time zone |           |          | 
 created_by_id | integer                        |           |          | 
 updated_by_id | integer                        |           |          | 
 locale        | character varying(255)         |           |          | 
Indexes:
    "pieces_pkey" PRIMARY KEY, btree (id)
    "pieces_created_by_id_fk" btree (created_by_id)
    "pieces_documents_idx" btree (document_id, locale, published_at)
    "pieces_updated_by_id_fk" btree (updated_by_id)
Foreign-key constraints:
    "pieces_created_by_id_fk" FOREIGN KEY (created_by_id) REFERENCES admin_users(id) ON DELETE SET NULL
    "pieces_updated_by_id_fk" FOREIGN KEY (updated_by_id) REFERENCES admin_users(id) ON DELETE SET NULL
Referenced by:
    TABLE "ml_image_metadatas_piece_lnk" CONSTRAINT "ml_image_metadatas_piece_lnk_ifk" FOREIGN KEY (piece_id) REFERENCES pieces(id) ON DELETE CASCADE
    TABLE "pieces_game_lnk" CONSTRAINT "pieces_game_lnk_fk" FOREIGN KEY (piece_id) REFERENCES pieces(id) ON DELETE CASCADE

wopr-db=> \d ml_image_metadatas
                                            Table "public.ml_image_metadatas"
     Column      |              Type              | Collation | Nullable |                    Default             
        
-----------------+--------------------------------+-----------+----------+----------------------------------------
--------
 id              | integer                        |           | not null | nextval('ml_image_metadatas_id_seq'::re
gclass)
 document_id     | character varying(255)         |           |          | 
 filename        | character varying(255)         |           |          | 
 uid             | character varying(255)         |           |          | 
 create_time     | timestamp(6) without time zone |           |          | 
 update_time     | timestamp(6) without time zone |           |          | 
 object_rotation | integer                        |           |          | 
 object_position | character varying(255)         |           |          | 
 color_temp      | character varying(255)         |           |          | 
 light_intensity | character varying(255)         |           |          | 
 created_at      | timestamp(6) without time zone |           |          | 
 updated_at      | timestamp(6) without time zone |           |          | 
 published_at    | timestamp(6) without time zone |           |          | 
 created_by_id   | integer                        |           |          | 
 updated_by_id   | integer                        |           |          | 
 locale          | character varying(255)         |           |          | 
Indexes:
    "ml_image_metadatas_pkey" PRIMARY KEY, btree (id)
    "ml_image_metadatas_created_by_id_fk" btree (created_by_id)
    "ml_image_metadatas_documents_idx" btree (document_id, locale, published_at)
    "ml_image_metadatas_updated_by_id_fk" btree (updated_by_id)
Foreign-key constraints:
    "ml_image_metadatas_created_by_id_fk" FOREIGN KEY (created_by_id) REFERENCES admin_users(id) ON DELETE SET NUL
L
    "ml_image_metadatas_updated_by_id_fk" FOREIGN KEY (updated_by_id) REFERENCES admin_users(id) ON DELETE SET NUL
L
Referenced by:
    TABLE "ml_image_metadatas_game_lnk" CONSTRAINT "ml_image_metadatas_game_lnk_fk" FOREIGN KEY (ml_image_metadata
_id) REFERENCES ml_image_metadatas(id) ON DELETE CASCADE
    TABLE "ml_image_metadatas_piece_lnk" CONSTRAINT "ml_image_metadatas_piece_lnk_fk" FOREIGN KEY (ml_image_metada
ta_id) REFERENCES ml_image_metadatas(id) ON DELETE CASCADE

```