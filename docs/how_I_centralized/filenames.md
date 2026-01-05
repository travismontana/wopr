# filenames

The database will control the filenames for mlcaptures.

Just need to POST to the api:
pieces_id
game_catalog_id
lightSetting.temp{'nameId'}
lightSetting.intensity[id]
object.rotations[id]
object.position{'nameId'}
timestamp

Then directus will create the filename for you which will be
filenames.mlcapture{'fullImageFilename'} for the full name
and
filenames.mlcapture{'thumbnailFilename'} for the thumbnail name

  "filenames": {
    "mlcapture": {
      "fullImageFilename": "{{pieces_id}}-{{game_catalog_id}}-{{capture_id}}.jpg",
      "thumbnailFilename": "{{pieces_id}}-{{game_catalog_id}}-{{capture_id}}-thumb.jpg"

where capture_id is the uuid generated for the row inserted into mlimages.

I want directus to use that to generate the filename