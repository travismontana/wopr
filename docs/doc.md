# WOPR - Worldstate Observation and Prediction Resource

## WOPR 2.0

### Previous Version:
- 0.0 - concept
- 1.0 - web based
- 2.0 - pyside based

## What
What is WOPR? WOPR tracks tabletop game state through computer vision. Players use an interface to capture images of their game board. WOPR analyzes the images, detects game pieces, validates moves against rules, and maintains a complete game history.

## Nitty Gritty
The captured images will pass through a pipeline/databus so they can be analyzed when needed.
the rate will be 4Hz-ish.  4 times a second, the app will grab the current image from the defined usb web cam, and place it in the bus.  
anything that needs to work on that image, can.  The idea is that there will be a calibration set at the beginning of the game, and the images will need to pass through each step (each thread will pull the image it needs from the bus)

User starts wopr (./wopr.py), they are presented with the app, already on the calibration screen.  They see what the camera is seeing, adn adjusts the settings for the light and such.  they click save.

They can then:
1. View  previous games via the "Sessions" screen
2. Create a new session
3. edit settings.

When they want to create a new session, they will enter who's playing, what game they are playing, and any other details, then click start.
Then the app will bring up the "Run" screen, where it shows how the current player is, what the previous moves were, has links to the previous moves, boxes to enter any notes on the current move, a button to capture the current move

images captured and processes:
start of game
each move
final move of the game

Each time an image is captured, it's passed through the whole pipeline, inference, cell detection, etc.., then all the moves made so far are given to Ludii, whcih will then "Play" that game to make sure moves were legal (you check on each move), and if you want a hint, it can run the game until each player has won, tracking how it did that, then give it back to the main app to show the user.

I have a basic app created, it starts and shows the main window with tabs for the settings/calibration/runs/library

I'm at the point now where I need to create the bus, do the threading, etc...

I know we've been working on this, but I think this will be a start from zero (zero = where I'm at with the basic app currently)

I need to visualize how this will work, and what I need to do, preferably in order.

SDLC is too much, but let's come up with the docs I need to do this.