DESCRIPTION = '''You need to play a puzzle named 'Sudokill' against another player. Sudokill is a 2-player twist on the classic Sudoku game. As in a traditional Sudoku game, you are given a grid. The goal is to fill the grid with numbers so that each row, column, and subgrid contains all numbers from 1 to length of row/column without repetition.

In Sudokill, the additional rule for this two-player game is: Players alternate placing numbers on the board. The first player can place a number in any unoccupied space. After that, each player must place their number in an unoccupied space in either the same row or column as the last move. If there are no such available spaces, the player can place a number anywhere on the board. The first player to make a move that violates the rules loses.

The grid has some cells pre-filled with numbers. At each turn, you will be given an image containing a grid, and you should fill only one empty cell. 

For example, if the current grid is 

[[6, 8, 4, 5, 1, 3, 2, 7, 9],
[5, 9, 7, 6, 2, 0, 1, 8, 0],
[2, 3, 1, 4, 8, 7, 6, 5, 0],
[9, 1, 2, 7, 6, 4, 8, 0, 3],
[4, 6, 8, 3, 0, 1, 7, 2, 5],
[7, 5, 3, 2, 9, 8, 4, 1, 6],
[8, 4, 5, 1, 3, 2, 9, 6, 7],
[1, 0, 6, 9, 0, 5, 0, 3, 8],
[3, 2, 0, 0, 7, 0, 5, 4, 0]]

(value 0 means empty cell) and now is your turn and the previous move by the opponent is to fill the cell at (0, 8) with the value 9. So now the cells you can place a number are [(1,8), (2,8), (8,8)] because you can only place a number in the same row or column as the last move.

For example, if the current grid is

[[6, 8, 4, 5, 1, 3, 2, 7, 9],
[5, 9, 7, 6, 2, 0, 1, 8, 0],
[2, 3, 1, 4, 8, 7, 6, 5, 0],
[9, 1, 2, 7, 6, 4, 8, 0, 3],
[4, 6, 8, 3, 0, 1, 7, 2, 5],
[7, 5, 3, 2, 9, 8, 4, 1, 6],
[8, 4, 5, 1, 3, 2, 9, 6, 7],
[1, 0, 6, 9, 0, 5, 0, 3, 8],
[3, 2, 0, 0, 7, 0, 5, 4, 1]]

and now is your turn and the previous move by the opponent is to fill the cell at (0, 8) with the value 9. Now you can fill the cell (1, 8) with the value 4 to win this game because after you fill the cell (1, 8) with the value 4, the opponent can only fill the cell (2, 8) and (1, 5), but no matter which value the opponent fills in these two cells will violate the rules.

Provide your output in the following format:

Reasoning: Explain the reasoning behind your choice of cell and value, aiming to place your opponent at a disadvantage.

Operation: Specify the cell to be filled and the value to be placed in the format: `operation = [(row_index, column_index), value]`. Please note that the row_index and column_index are 0-based index.''' 

SIMPLIFIED_DESCRIPTION = None

STATE_TRANSIT_PROMPT = None

PUZZLE_INTRO = '''Game Description
        
Game: Sudokill
        
Overview:
Sudokill is a competitive two-player variation of the classic Sudoku game. The game features a standard grid, and the objective remains to fill the grid so that each row, column, and ubgrid contains all numbers from 1 to the length of row/column without repetition.

Mechanics:
1. Grid Setup: The game begins with a grid, some cells of which are pre-filled with numbers. Unoccupied cells are represented by 0.
2. Turn-Based Play: Players alternate turns placing numbers on the board.
- The first player can place a number in any unoccupied space.
- Subsequent moves must be placed in an unoccupied space within the same row or column as the last move. If no such space is available, the player may place a number anywhere on the board.
3. Winning Condition: A player loses if they make a move that violates the rules.'''