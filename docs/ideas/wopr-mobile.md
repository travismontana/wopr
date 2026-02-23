# wopr-mobile

board
camera
laptop

- UI
    - Games
    - Images
    - Sessions
    - Players
    - (info preloaded)

## Play a game session:
* New game session ->
* Select game -> (load info)
* Num Players ->
* Add Plyaers to round ->
* Do the rounds/games

* See what sessions are local
=======
## Images
* See what images are local
* Add images
=======
## Games:
* See what there is already
* Add new
=======
## Players:
* Same

===========================================
## general idea
Can do the things that wopr does, just mobile.

A UI (django), libraries for all the functions.

Be able to do live infernece would be cool.

So, the UI can do things local witht he camera and storage
so it doesnt have to deal with NFS.

Thinking a full os.
Browse to cool dns https://wopr
Main site: woprw
BOH: boh.wopr

Sync to core? or export/import or "marketplace" where images/games are shared or just give it a .lud and a model.

Yea, just give it a lud and a model (that can the package to load) then it can do things.

when it comes back, just export, clean it, go.

the import can be into wopr-core

so there it is.

wopr-core is wopr-web, wopr-model - this is the part that builds the model and manages the core stuff, can talk to wopr-cam and do what wopr-mobile does.
wopr-mobile - wopr-core, but cleaned up basically.  The start of wopr v2.

meta modules:
wopr-core
wopr-mobile

wopr-core modules:
wopr-web - core UI
wopr-db - main big database
wopr-cam 
wopr-model
wopr-api
wopr-filebrowser
wopr-images
wopr-imagesproxy
wopr-labelstudio
wopr-monitoring
wopr-openwebui
wopr-spoolman

wopr-mobile modules:
wopr-web
wopr-db - just needs the schema and min data
wopr-cam
wopr-model - just needs ultralytics part
wopr-images
wopr-imagesproxy

In fact in the installer?  maybe you select what to install.

There will be more modules, but that's what I have so far.