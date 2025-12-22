Workflows:

The main UI is broken into:
Main page/
|- dashboard/
|- game/
|- ml/
|- control/

Dashboard:
React (Dashboard.tsx)
Shows what games are in progress
Can start games
Shows the status of the systems

Games:
React (games.tsx)
start/stop games
edit games
replay/

ML:
ML/Capture:
* in UI, select ML, then capture
* in captrure it has the available games/pieces to change the traning images, add new, delete, list, view
* It knows the games, then what pieces are part of each game, and what images belong to each game
* has predefined template of what images it's expecting (all the rotations, position on the table, etc...) for each piece, game, etc...
for each piece, it's linked back to which game it's for
tracking what images are for waht pieces are for what games is all tracked in the database

ML/Train:

Control:
* Add/remove users
* Edit config
* Edit DB data (CURD interface)
* start/stop/update services (future)
