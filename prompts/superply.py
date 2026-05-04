DESCRIPTION = '''You are required to play a game called Superply with another player. This is a path-building board game played on a grid. The objective for Player 1 is to construct a path from the left side of the grid to the right, while Player 2 must build a path from the top to the bottom. A valid path is a sequence of adjacent same-value squares, where each square in the path must touch the next one either by a side or a corner.

During each turn, a player claims a square by selecting a grid position that satisfies the system-provided hint. If the chosen position is invalid, no changes are made, and the turn passes to the other player.

The hints are mathematical operations, such as "sum is less than 10," meaning that the sum of the numbers in the selected position must be less than 10 (row_indx + column_index < 10). A player may choose any grid position that satisfies the given hint and is unoccupied.

The game board is a grid, and it is 1-indexed. Initially, all grid values are set to 0. When a player correctly selects a grid position, the value of that position changes: 1 for Player 1, and 2 for Player 2. The first player to successfully build their path wins the game.

For example, if the hint is "product contains digit 6," and the grid is as follows:
[[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0]]

If you are Player 1, you can select the position (1, 6), (6, 1), (2, 3), (3, 2) or (6, 6) because the product of the row and column indices is 6, 6, 6, 6 and 36, respectively, and they all contain the digit 6.

If you choose the position (6, 6), the grid becomes:
[[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 1]]

Please provide your actions in the following format:

Reasoning: Explanation of your choice.
Operation: Specify the position on the grid in the format: `operation = (row_index, column_index)`.\n\n''' 

SIMPLIFIED_DESCRIPTION = None

STATE_TRANSIT_PROMPT = None

CODE_PROMPT = '''You are about to play a game called **Superply** against an opponent.

Rules
-----
1. The game is played on a 1-indexed grid, where all squares are initially set to 0.
2. Player 1 aims to build a path connecting the **left side** of the grid to the **right side**.
3. Player 2 aims to build a path connecting the **top side** of the grid to the **bottom side**.
4. A valid path consists of adjacent same-value squares (touching by sides or corners).
5. On your turn, you must select an unoccupied grid position that satisfies the system-provided **hint**.
6. If you select an invalid or occupied position, no change is made, and the turn passes.
7. When a player selects a valid position, the grid cell is updated to 1 (for Player 1) or 2 (for Player 2).
8. The first player to successfully build a complete path wins the game.

Hints
-----
Hints are mathematical conditions based on the row and column indices. The allowed operations and conditions include:
- Operations: `['sum', 'product', 'difference']`
- Conditions: `['is less than v1', 'is greater than v1', 'contains digit v1', 'is even', 'is odd', 'is between v1 and v2, inclusive']`

For example, a hint "sum is less than 6" means you can select a position where (row_index + column_index) < 6.

Example  
--------
Suppose the hint is "product contains digit 6" and the grid is empty:

[[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]

As Player 1, you can select (1,6), (2,3), (3,2), (6,1), or (6,6) because their products are 6, 6, 6, 6, and 36, respectively—all containing the digit 6.

If you choose (6,6), the grid updates to:

[[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1]]


Task
----
Implement a Python strategy that, given the current `current_grid`, `current_hint`, and `player_idx`, returns the best position to select next.

**Input Format:**
- `current_grid`: a list of lists of integers, representing the current board state.
- `current_hint`: a string describing the current allowed move condition. The hint is maked up one of the operations and one of the conditions: operation + ' ' + condition. For example, "sum is less than 10" or "product contains digit 6".
- `player_idx`: an integer, 1 or 2, indicating which player you are.

**Output Format:**
- Return a tuple `(row_index, column_index)`, where both indices are integers representing the selected grid position.

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

class SuperplyCustomStrategy:
    def __init__(self, model: BaseStrategy):
        self._model = model
        self.name = self._model.name
        self.history = self._model.history
        self.strategy_type = StrategyType.Custom
    
    def update_model_field(self, field_name: str, value: Any):
        if hasattr(self._model, field_name):
            setattr(self._model, field_name, value)

    def receive_message(self, message: Info) -> Info:
        # current_grid is a list of lists of integers
        current_grid = message.message[0].data[0]
        # current_hint is a string
        current_hint = message.message[0].data[1]
        # player_idx is an integer: 1 or 2
        player_idx = message.message[0].data[2]

        # return a tuple (row_index, column_index), both are integers
        position_selected = None
        # TODO: implement your decision logic here

        return Info(
            sender=self.__class__.__name__,
            receiver=message.sender,
            difficulty=message.difficulty,
            message=[BaseMessageDataType(data=position_selected, type='custom')]
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

- `reasoning` — concise explanation of how you determined `position_selected`.
* `code` — complete, syntax-error-free Python implementing the decision logic, with **no** ```python fences or other formatting.
'''


PUZZLE_INTRO = '''Game Description
        
Game: Superply
        
Overview:
Superply is a two-player path-building board game played on a 6x6 grid. Player 1’s objective is to construct a path from the left side of the grid to the right, while Player 2 must build a path from the top to the bottom. Each player takes turns claiming grid positions based on system-provided mathematical hints. A valid path consists of adjacent same-value squares, either by a side or corner. Player 1 marks claimed positions with a value of 1, and Player 2 with a value of 2. The first player to complete their path wins.

Mechanics:
1. Grid and Path Construction:
- The grid is initially filled with zeros.
- Player 1 must construct a path from the left side (column 1) to the right side (column 6).
- Player 2 must build a path from the top (row 1) to the bottom (row 6).

2. Hints and Valid Moves:
- On each turn, players receive a mathematical hint, such as "sum is less than 10" or "product contains digit 6."
- Players can select any unclaimed grid position that satisfies the hint to claim.
- If the selected position does not satisfy the hint, the turn is skipped.

3. Objective:
- Each player claims grid positions by following the hints.
- The winner is the first player to successfully build a valid path across the grid.'''