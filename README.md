# sigil
Daemon and client for the online Sigil game

This is an online version of my board game "Sigil". I have been tinkering with the design of Sigil as a physical board game
for about 10 years. This digital version was created in the past month, as a coding exercise & a way to play the game
with remote friends.

To launch the game, type "docker-compose build && docker-compose up" into the command line. This will launch the Sigil daemon.
(Sometimes it takes a couple tries before it builds properly.) The first player to connect will be Red, the second player 
to connect will be Blue, and the game begins once both are connected.
