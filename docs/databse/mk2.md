gameCatalog
pieces
MLimagemetadata
{
  "errors": [
    {
      "message": "alter table \"game_catalog\" add constraint \"game_catalog_name_foreign\" foreign key (\"name\") references \"pieces\" (\"id\") on delete SET NULL - foreign key constraint \"game_catalog_name_foreign\" cannot be implemented",
      "extensions": {
        "code": "INTERNAL_SERVER_ERROR"
      }
    }
  ]
}