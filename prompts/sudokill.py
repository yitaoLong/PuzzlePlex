DESCRIPTION = '''You need to play a puzzle named 'Sudokill' against another player. Sudokill is a 2-player twist on the classic Sudoku game. As in a traditional Sudoku game, you are given a grid. The goal is to fill the grid with numbers so that each row, column, and subgrid contains all numbers from 1 to length of row/column without repetition.

In Sudokill, the additional rule for this two-player game is: Players alternate placing numbers on the board. The first player can place a number in any unoccupied space. After that, each player must place their number in an unoccupied space in either the same row or column as the last move. If there are no such available spaces, the player can place a number anywhere on the board. The first player to make a move that violates the rules loses.

The grid has some cells pre-filled with numbers. Unoccupied cells are represented by 0. The input is a 2D list of integers representing the grid, using 0-based indexing. At each turn, you should fill only one empty cell. 

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

and now is your turn and the previous move by the opponent is to fill the cell at (0, 8) with the value 9. So now the cells you can place a number are [(1,8), (2,8), (8,8)] because you can only place a number in the same row or column as the last move.

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

Operation: Specify the cell to be filled and the value to be placed in the format: `operation = [(row_index, column_index), value]`.\n\n
The initial grid is {grid}.\n''' 

SIMPLIFIED_DESCRIPTION = '''You need to play a puzzle named 'Sudokill' against another player. Sudokill is a 2-player twist on the classic Sudoku game. As in a traditional Sudoku game, you are given a grid. The goal is to fill the grid with numbers so that each row, column, and subgrid contains all numbers from 1 to length of row/column without repetition.

In Sudokill, the additional rule for this two-player game is: Players alternate placing numbers on the board. The first player can place a number in any unoccupied space. After that, each player must place their number in an unoccupied space in either the same row or column as the last move. If there are no such available spaces, the player can place a number anywhere on the board. The first player to make a move that violates the rules loses.

The grid has some cells pre-filled with numbers. Unoccupied cells are represented by 0. The input is a 2D list of integers representing the grid, using 0-based indexing. At each turn, you should fill only one empty cell. Provide your output in the following format:

Reasoning: Explain the reasoning behind your choice of cell and value, aiming to place your opponent at a disadvantage.

Operation: Specify the cell to be filled and the value to be placed in the format: `operation = [(row_index, column_index), value]`.\n\n
The initial grid is {grid}.\n'''

STATE_TRANSIT_PROMPT = '''Your competitive move is to fill the cell at ({row_index}, {col_index}) with the value {value}. Now the grid becomes {grid}. Now it is your turn.'''

CODE_PROMPT = '''You are about to play a game called **Sudokill** against an opponent.

Rules
-----
1. You are given an initial Sudoku grid (N x N), where N is divisible by the square root of N.
2. The goal is to fill the grid so that each row, column, and √N x √N subgrid contains all numbers from 1 to N without repetition.
3. Players alternate placing one number on the board in an empty cell (represented as 0).
4. The first player may place a number in any empty cell.
5. Subsequent players must place their number in an empty cell within the same **row or column** as the **last move**.
6. If there are no valid empty cells in the same row or column, the player may move **anywhere** on the board.
7. If a player makes a move that violates the Sudoku rules (e.g., duplicates in row/column/subgrid), they **immediately lose**.

Example  
--------
Grid:
[[6, 8, 4, 5, 1, 3, 2, 7, 9],  
 [5, 9, 7, 6, 2, 0, 1, 8, 0],  
 [2, 3, 1, 4, 8, 7, 6, 5, 0],  
 [9, 1, 2, 7, 6, 4, 8, 0, 3],  
 [4, 6, 8, 3, 0, 1, 7, 2, 5],  
 [7, 5, 3, 2, 9, 8, 4, 1, 6],  
 [8, 4, 5, 1, 3, 2, 9, 6, 7],  
 [1, 0, 6, 9, 0, 5, 0, 3, 8],  
 [3, 2, 0, 0, 7, 0, 5, 4, 0]]

Previous move: (0, 8) → 9  
You can now play in: (1, 8), (2, 8), (8, 8)  

Suppose you play (1, 8) → 4. Then opponent has only (2, 8) and (1, 5) to choose from. Any number they place violates Sudoku rules, and they lose. So (1, 8) → 4 is a **winning move**.

Task
----
Implement a Python strategy that, given the current `grid` and `prev_move`, returns the best move in the form `[(row_index, column_index), value]`.

**Input Format:**  
- `prev_move`: Either None or a list `[(row_index, column_index), value]`  
- `grid`: A 2D list of integers representing the current Sudoku board (0 = empty)

**Output Format:**  
- Return a list `[(row_index, column_index), value]` representing your move

You should also consider the computational efficiency of your program—if it runs for more than 5 minutes, you will lose the game.

Template
----------------------------------------
from pydantic import BaseModel  
from typing import List, Optional, Dict, Any  
from enum import Enum  
from abc import abstractmethod  

from system.message import Info  
from system.message import BaseMessageDataType  
from model.strategy_type import StrategyType  
from model.base import BaseStrategy  


class SudoKillCustomStrategy:  
    def __init__(self, model: BaseStrategy):  
        self._model = model  
        self.name = self._model.name  
        self.history = self._model.history  
        self.strategy_type = StrategyType.Custom  
    
    def update_model_field(self, field_name: str, value: Any):  
        if hasattr(self._model, field_name):  
            setattr(self._model, field_name, value)  

    def receive_message(self, message: Info) -> Info:  
        # grid is list of list, with each list is int     
        grid = message.message[0].data[1]             
        # prev_move is [(row_index, col_index), value], if you are the first move, it is None
        prev_move = message.message[0].data[0]  
        # return the decision with the format [(row_index, col_index), value]  
        move = None  
        # TODO: implement your decision logic here  

        return Info(  
            sender=self.__class__.__name__,  
            receiver=message.sender,  
            difficulty=message.difficulty,  
            message=[BaseMessageDataType(data=move, type='custom')]  
        )  

Guidelines
----------
* The existing template should not be modified. You can add variables, functions, or classes as needed, for example you may add helper variables or logic to track card usage, past moves, etc.
* You can import additional libraries and assume any additional libraries are already installed. 

Required Output Format
----------------------
Return a single JSON object:

{
  "reasoning": "<your step-by-step explanation>",
  "code": "<only the Python code and the code must be complete that including code in template>"
}

* `reasoning` — Explain why you chose this move and how it weakens your opponent's future options.
* `code` — complete, syntax-error-free Python implementing the decision logic, with **no** ```python fences or other formatting.
'''

ONE_SHOT_PROMPT = '''You need to play a puzzle named 'Sudokill' against another player. Sudokill is a 2-player twist on the classic Sudoku game. As in a traditional Sudoku game, you are given a grid. The goal is to fill the grid with numbers so that each row, column, and subgrid contains all numbers from 1 to length of row/column without repetition.

In Sudokill, the additional rule for this two-player game is: Players alternate placing numbers on the board. The first player can place a number in any unoccupied space. After that, each player must place their number in an unoccupied space in either the same row or column as the last move. If there are no such available spaces, the player can place a number anywhere on the board. The first player to make a move that violates the rules loses.

The grid has some cells pre-filled with numbers. Unoccupied cells are represented by 0. The input is a 2D list of integers representing the grid, using 0-based indexing. At each turn, you should fill only one empty cell.

Here is one example of the game:

Initial grid:
[[0, 3, 0, 8, 6, 0, 9, 2, 7],
 [2, 9, 4, 3, 0, 7, 0, 0, 0],
 [7, 0, 8, 1, 0, 9, 5, 0, 4],
 [3, 8, 6, 9, 7, 0, 4, 0, 1],
 [1, 0, 2, 0, 0, 8, 6, 0, 3],
 [0, 4, 0, 6, 0, 3, 2, 7, 8],
 [8, 1, 0, 2, 0, 0, 0, 4, 0],
 [0, 0, 0, 7, 8, 5, 1, 0, 0],
 [6, 5, 7, 0, 9, 0, 3, 8, 0]]

You move first:
1. You place 5 at (0, 0): [[5, 3, 0, 8, 6, 0, 9, 2, 7], ...]
   Reasoning: As the first player, I choose (0, 0) with 5 to add constraints to row 0 and column 0 without completing any row, column, or subgrid, limiting the opponent's options.
2. Your opponent places 1 at (0, 2): [[5, 3, 1, 8, 6, 0, 9, 2, 7], ...]
3. You place 4 at (0, 5): [[5, 3, 1, 8, 6, 4, 9, 2, 7], ...]
   Reasoning: Placing 4 at (0, 5) in row 0 adds constraints to row 0 and the top-center subgrid, maintaining pressure without completing any structure.
4. Your opponent places 2 at (3, 5): [[5, 3, 1, 8, 6, 4, 9, 2, 7], ..., [3, 8, 6, 9, 7, 2, 4, 0, 1], ...]
5. You place 5 at (3, 7): [[5, 3, 1, 8, 6, 4, 9, 2, 7], ..., [3, 8, 6, 9, 7, 2, 4, 5, 1], ...]
   Reasoning: Placing 5 at (3, 7) in row 3 constrains row 3 and column 7, limiting the opponent's valid moves.
6. Your opponent places 1 at (1, 7): [[5, 3, 1, 8, 6, 4, 9, 2, 7], [2, 9, 4, 3, 0, 7, 0, 1, 0], ...]
7. You place 5 at (1, 4): [[5, 3, 1, 8, 6, 4, 9, 2, 7], [2, 9, 4, 3, 5, 7, 0, 1, 0], ...]
   Reasoning: Placing 5 at (1, 4) in row 1 restricts row 1 and the middle-left subgrid, reducing the opponent's flexibility.
8. Your opponent places 2 at (2, 4): [[5, 3, 1, 8, 6, 4, 9, 2, 7], [2, 9, 4, 3, 5, 7, 0, 1, 0], [7, 0, 8, 1, 2, 9, 5, 0, 4], ...]
9. You place 6 at (2, 1): [[5, 3, 1, 8, 6, 4, 9, 2, 7], [2, 9, 4, 3, 5, 7, 0, 1, 0], [7, 6, 8, 1, 2, 9, 5, 0, 4], ...]
   Reasoning: Placing 6 at (2, 1) in row 2 constrains row 2 and column 1, maintaining strategic pressure.
10. Your opponent places 7 at (4, 1): [[5, 3, 1, 8, 6, 4, 9, 2, 7], ..., [1, 7, 2, 0, 0, 8, 6, 0, 3], ...]
11. You place 5 at (4, 3): [[5, 3, 1, 8, 6, 4, 9, 2, 7], ..., [1, 7, 2, 5, 0, 8, 6, 0, 3], ...]
    Reasoning: Placing 5 at (4, 3) in row 4 adds constraints to row 4 and the central subgrid, limiting opponent options.
12. Your opponent places 4 at (4, 4): [[5, 3, 1, 8, 6, 4, 9, 2, 7], ..., [1, 7, 2, 5, 4, 8, 6, 0, 3], ...]
13. You place 9 at (4, 7): [[5, 3, 1, 8, 6, 4, 9, 2, 7], ..., [1, 7, 2, 5, 4, 8, 6, 9, 3], ...]
    Reasoning: Placing 9 at (4, 7) in row 4 constrains row 4 and column 7, reducing the opponent's valid moves.
14. Your opponent places 3 at (2, 7): [[5, 3, 1, 8, 6, 4, 9, 2, 7], [2, 9, 4, 3, 5, 7, 0, 1, 0], [7, 6, 8, 1, 2, 9, 5, 3, 4], ..., [1, 7, 2, 5, 4, 8, 6, 9, 3], ...]
15. You place 9 at (2, 0), but this is not a valid move as it violates the rules of Sudokill. Thus, you lose the game.

Now the game starts, and the initial grid is: {grid}.

Provide your output in the following format:

Reasoning: Explain the reasoning behind your choice of cell and value, aiming to place your opponent at a disadvantage.

Operation: Specify the cell to be filled and the value to be placed in the format: `operation = [(row_index, column_index), value]`.'''

VOTE_PROMPT = '''This time you are provided several choices of which cell to fill and which value to place. You must choose one of them.'''

WITHOUT_HISTORY_PROMPT = '''You need to play a puzzle named 'Sudokill' against another player. Sudokill is a 2-player twist on the classic Sudoku game. As in a traditional Sudoku game, you are given a grid. The goal is to fill the grid with numbers so that each row, column, and subgrid contains all numbers from 1 to length of row/column without repetition.

In Sudokill, the additional rule for this two-player game is: Players alternate placing numbers on the board. The first player can place a number in any unoccupied space. After that, each player must place their number in an unoccupied space in either the same row or column as the last move. If there are no such available spaces, the player can place a number anywhere on the board. The first player to make a move that violates the rules loses.

The grid has some cells pre-filled with numbers. Unoccupied cells are represented by 0. The input is a 2D list of integers representing the grid, using 0-based indexing. At each turn, you should fill only one empty cell. 

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

and now is your turn and the previous move by the opponent is to fill the cell at (0, 8) with the value 9. So now the cells you can place a number are [(1,8), (2,8), (8,8)] because you can only place a number in the same row or column as the last move.

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

Operation: Specify the cell to be filled and the value to be placed in the format: `operation = [(row_index, column_index), value]`.\n\n

Your opponent previous move is to fill the cell at ({row_index}, {col_index}) with the value {value}. Now the grid becomes {grid}. Now it is your turn.'''

LEGAL_CANDIDATES_PROMPT = '''To help you better making decision, you are provided a list of legal moves, which means when you take these moves, it will not let you lose directly. You can choose one of them or you can choose a move that is not in the list if you think it is better. Here is the list of legal moves: {legal_moves}.'''

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