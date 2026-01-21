# Flows

## Model

is_downloaded?
is_backed_up?
has_config?
distfile_location = 

```
1_model_file:
    webui:
        - header display table:
          |--------------------------------------------------------------|
          | model name | is_downloaded | is_backed_up | has_config       |
          | shortname  |       checksums match?       | config_backed_up |
          |--------------------------------------------------------------|
        - main table:
```
| shortname | status placeholder | actions |
|:---------:|:------------------:|:-------:|
| wopr1 | | Download (if not downloaded) |
| | | Backup |
| | | Backup config |
```
        - Buttons: Download; Backup; Backup config
    model_api:
        - Validate path exists
        - if download, download
        - if backup, backup
        - if backup config, backup config
```
