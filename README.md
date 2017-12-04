# sigil
Daemon and client for the online Sigil game


What Is Sigil?

Sigil is a strategy board game in which two players, Red and Blue, battle for control of a magical 'spell circle'. The board is randomly generated at the beginning of each game, but other than this initial setup, the gameplay itself has no randomness & no hidden information.  I have been designing Sigil as a physical board game for about 10 years and have had over a dozen dedicated playtesters throughout this process.


What's In This Repo?

This repo is an online version of the game. The 'api' folder contains the back-end game logic (written in Python), and the clients/www/static folder contains the front-end GUI (written in JavaScript/HTML/CSS).


How Do I Play?

To start a game: With Docker installed, and in the main directory (with the 'docker-compose.yml' file): type

docker-compose build && docker-compose up

into the terminal. This will launch the daemon, which will be listening on some port (for me it is port 8000), and
you should then be able to navigate to it on a browser (by typing, e.g., "localhost:8000" into the address bar).
The first player to join will be Red, the second player to join will be Blue.
