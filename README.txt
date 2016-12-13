Game: Sorasu
Version: 1.0
Author: Mark Wissink

Sorasu was a learning project for programming in Python, it is a very simple game with some advanced features

------Features to note-------
custom physics library - makes use of the SAT Theorem to detect/resolve collisions.		
-physics.py
	
delta time physics bind - all physical movement is bound to delta time. It updates the game physics based on frame rate.		
-main.py
	
game object inheritance - all objects in game inherit from each other, creating an inheritance tree		
-game_object.py, player.py, and enemy.py

main files - three main states of the game are menu, editor, and game. They are responsible for running game logic
-menu.py, editor.py, and game.py

------------GUI--------------
The GUI for the game can be found in the initialize_menu function of both game.py and editor.py
menu.py also has GUI initialized in its __init__ function

GUI consists of the Button class and Textbox class, built to make up for the lack of GUI API in pygame
-button.py and textbox.py