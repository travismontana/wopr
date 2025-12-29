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