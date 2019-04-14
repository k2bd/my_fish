# How to play:
![Rules (pdf)](https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=2&cad=rja&uact=8&ved=2ahUKEwiP3PftuM_hAhU2SxUIHexBAt4QFjABegQIBBAC&url=https%3A%2F%2Fwww.fantasyflightgames.com%2Fffg_content%2Fhey-thats-my-fish-board-game%2Fhey-thats-my-fish-rulebook.pdf&usg=AOvVaw07sWl7C1ncESqZMjQyPqKi)

Click on a piece to select it and again to move it. Click an invalid move to deselect. Player types are defined by the players array passed to the app's init. Game board size also controlled there. Initial positions are currently randomized.

![points](https://user-images.githubusercontent.com/9196372/56091917-05225500-5ead-11e9-88f8-c1ce21b60ced.png)

# Bot rules:
 - Only do stuff between `get_move` being called and you returning an action - no calculating on someone else's turn
 - Do whatever you want about parallelizing it, spawning subprocesses, calling external libraries
 - Return a move within the time limit or a random move will be made

# TODO:
 - Currently expanding the game tree involves a deep copy of the whole gameBoard. This can be vastly improved with a simpler game state.
 - Trivial MCTS bot doesn't work, no idea why.
 - Network play is in the works.
 - Control over starting positions.
