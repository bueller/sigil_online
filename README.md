# sigil
Daemon and client for the online Sigil game

This is an online version of my board game "Sigil". I have been tinkering with the design of Sigil as a physical board game
for about 10 years. This digital version was created more recently, as a coding exercise & a way to play the game
with remote friends.

I did not use any special frameworks for making games; everything was done essentially from scratch, as an exercise to teach myself about web development. The back-end game logic is written in Python and daemonized using Flask (100% by me).  The front-end JavaScript, html, css was also 100% written by me.  A friend then helped me put the resulting webapp in a Docker container and set up the Docker configuration files.

The game "Sigil" itself is my own design, and the image file of the Sigil game board was created by me using Inkscape. The image files for the spell circles and the red/blue stones were pulled from the internet.


To start a game: With Docker installed, and in the main directory (with the 'docker-compose.yml' file): type

docker-compose build && docker-compose up

into the terminal. This will launch the daemon, which will be listening on some port (for me it is port 8000), and
you should then be able to navigate to it on a browser (by typing, e.g., "localhost:8000" into the address bar).
The first player to join will be Red, the second player to join will be Blue.
