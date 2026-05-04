DESCRIPTION = '''Your task is to solve a puzzle named 'Tidy Tower'. You are given a tower consisting of {num_cubes} cubes, each of which has one of 4 colors. The goal is to align all cubes so that each color is the same vertically. A tower with such an alignment is called tidy.
Two kinds of operations are allowed:
1. Rotate a cube: Rotate a single cube, and all cubes above it rotate as well.
2. Rotate with holding: Rotate a cube and hold a cube above it, preventing it and the cubes above it from rotating.
The cube colors are represented by the letters R, Y, B, and G, corresponding to red, yellow, blue, and green respectively. The forward-facing side of each cube is indicated by the first letter in the sequence. The color sequence is in clockwise order.

For example, when the tower is represented as RGBYRGBYBGBGBG, and if I rotate cube index 1 and not hold the cube above it, the tower will be transformed to RRGBYRGBGRGRGR, but if I rotate cube index 1 and hold the cube above it, it will become RRBYRGBYBGBGBG.

Now, solve the puzzle to make the tower tidy: {tower}, the sides are arranged in clockwise order: R → Y → B → G.

The output format shoule strictly follow the following format:
Reasoning: Explain the logic used to solve the chosen cube, please remember that do not violate the rules of Tidy Tower.
Output: List[int]= [[Cube index, Rotation, Holding], [Cube index, Rotation, Holding], ...] cube index is the index of the cube to rotate. Index starts from 0 to {max_height}. 
Rotation is the clockwise rotation of the cube. Rotation is from 1 to 4, representing how many times the cube is rotated. The value of 1 means one clockwise rotation, 2 means two clockwise rotations, and so on. The value of 4 means four clockwise rotations, which is equivalent to no rotation. 'Hold or not' is a value of 0 or 1, representing whether to hold the cube above it or not.
'''

DESCRIPTION_ITERATIVE = '''Your task is to solve a puzzle named 'Tidy Tower'. You are given a tower consisting of {num_cubes} cubes, each of which has one of 4 colors. The goal is to align all cubes so that each color is the same vertically. A tower with such an alignment is called tidy.
Two kinds of operations are allowed:
1. Rotate a cube: Rotate a single cube, and all cubes above it rotate as well.
2. Rotate with holding: Rotate a cube and hold a cube above it, preventing it and the cubes above it from rotating.
The cube colors are represented by the letters R, Y, B, and G, corresponding to red, yellow, blue, and green respectively. The forward-facing side of each cube is indicated by the first letter in the sequence. The color sequence is in clockwise order.

For example, when the tower is represented as RGBYRGBYBGBGBG, and if I rotate cube index 1 and not hold the cube above it, the tower will be transformed to RRGBYRGBGRGRGR, but if I rotate cube index 1 and hold the cube above it, it will become RRBYRGBYBGBGBG.

Now, solve the puzzle to make the tower tidy: {tower}, the sides are arranged in clockwise order: R → Y → B → G. Please solve it iteratively and output one step at a time. For each step, you have to output a list containing three elements: the index of the cube to rotate, the number of clockwise rotations, and whether to hold the cube above it (1 for holding, 0 for not holding). The cube index starts from 0 to {max_height}. The rotation is from 1 to 4, representing how many times the cube is rotated. The value of 1 means one clockwise rotation, 2 means two clockwise rotations, and so on. The value of 4 means four clockwise rotations, which is equivalent to no rotation. 'Hold or not' is a value of 0 or 1, representing whether to hold the cube above it or not.

The output format shoule strictly follow the following format:
Reasoning: Explain the logic used to solve the chosen cube, please remember that do not violate the rules of Tidy Tower.
Operation: Specify one step in the format 'operation = [Cube index, Rotation, Holding]'.
'''

SIMPLIFIED_DESCRIPTION = '''Your task is to solve a puzzle named 'Tidy Tower'. You are given a tower consisting of {num_cubes} cubes, each of which has one of 4 colors. The goal is to align all cubes so that each color is the same vertically. A tower with such an alignment is called tidy.
Two kinds of operations are allowed:
1. Rotate a cube: Rotate a single cube, and all cubes above it rotate as well.
2. Rotate with holding: Rotate a cube and hold a cube above it, preventing it and the cubes above it from rotating.
The cube colors are represented by the letters R, Y, B, and G, corresponding to red, yellow, blue, and green respectively. The forward-facing side of each cube is indicated by the first letter in the sequence. The color sequence is in clockwise order.

Now, solve the puzzle to make the tower tidy: {tower}, the sides are arranged in clockwise order: R → Y → B → G.

The output format shoule strictly follow the following format:
Reasoning: Explain the logic used to solve the chosen cube, please remember that do not violate the rules of Tidy Tower.
Output: List[int]= [[Cube index, Rotation, Holding], [Cube index, Rotation, Holding], ...] cube index is the index of the cube to rotate. Index starts from 0 to {max_height}. 
Rotation is the clockwise rotation of the cube. Rotation is from 1 to 4, representing how many times the cube is rotated. The value of 1 means one clockwise rotation, 2 means two clockwise rotations, and so on. The value of 4 means four clockwise rotations, which is equivalent to no rotation. 'Hold or not' is a value of 0 or 1, representing whether to hold the cube above it or not.
'''

CODE_PROMPT = '''You are about to solve a puzzle called **Tidy Tower**.

Rules
-----
1. You are given a tower consisting of multiple cubes.
2. Each cube has four sides colored **Red (R)**, **Yellow (Y)**, **Blue (B)**, and **Green (G)** in clockwise order.
3. The front-facing color of each cube is indicated by the letter in the tower string.
4. Your goal is to **align the tower** so that all cubes at each vertical position show the same color — this is called a **tidy tower**.
5. You are allowed two kinds of operations:
   - **Rotate a cube**: Rotate a cube clockwise, which also rotates **all cubes above it**.
   - **Rotate with holding**: Rotate a cube **while holding** a cube above it (and any cubes above that one), so that only the lower cubes rotate.

Example
--------
Tower = RGBYRGBYBGBGBG (index 0 at the bottom)  
- If you **rotate** cube at index 1 without holding (holding = 0), the tower becomes:  
  `RRGBYRGBGRGRGR`
- If you **rotate** cube at index 1 and **hold** (holding = 1), the tower becomes:  
  `RRBYRGBYBGBGBG`

Task
----
Implement a Python strategy that, given the current `tower`, returns the sequence of operations needed to make the tower tidy.

**Input Format:**  
- `tower`: a list of strings where each element is one of `'R'`, `'Y'`, `'B'`, or `'G'`, representing the front-facing color of the cube from bottom (index 0) to top.

**Output Format:**  
- Return a list of lists `List[int]` where each inner list represents one move:  
  `[cube_index, rotation, hold]`  
  where:  
  - `cube_index`: integer (0-indexed from the bottom),
  - `rotation`: integer from 1 to 4 (1 = one clockwise turn, ..., 4 = no rotation),
  - `hold`: 0 or 1 (0 = no hold, 1 = hold the cube above it).

You should also consider the computational efficiency of your program—if it runs for more than 5 minutes, you will lose the game.

Template
----------------------------------------
from pydantic import BaseModel  
from typing import List, Optional, Tuple, Any  
from enum import Enum  
from abc import abstractmethod

from system.message import Info  
from system.message import BaseMessageDataType  
from model.strategy_type import StrategyType  
from model.base import BaseStrategy

class TidyTowerCustomStrategy:
    def __init__(self, model: BaseStrategy):
        self._model = model
        self.name = self._model.name
        self.history = self._model.history
        self.strategy_type = StrategyType.Custom
    
    def update_model_field(self, field_name: str, value: Any):
        if hasattr(self._model, field_name):
            setattr(self._model, field_name, value)

    def receive_message(self, message: Info) -> Info:
        # tower is a list of str, where each item is either 'G', 'R', 'B' or 'Y'
        tower = message.message[0].data
        all_operations = None
        # TODO: implement your decision logic here
        return Info(
            sender=self.__class__.__name__,
            receiver=message.sender,
            difficulty=message.difficulty,
            message=[BaseMessageDataType(data=all_operations, type='custom')]
        )

Guidelines
----------
* The existing template should not be modified. You can add variables, functions, or classes as needed.
* You can import additional libraries and assume they are already installed.

Required Output Format
----------------------
Return a single JSON object:

{
  "reasoning": "<your step-by-step explanation>",
  "code": "<only the Python code and the code must be complete that including code in template>"
}

* `reasoning` — concise explanation of how you determined the operations to tidy the tower, making sure not to violate the rules of rotation and holding.
* `code` — complete, syntax-error-free Python implementing the decision logic, with **no** ```python fences or other formatting.
'''

ONE_SHOT_PROMPT = '''Your task is to solve a puzzle named 'Tidy Tower'. You are given a tower consisting of {num_cubes} cubes, each of which has one of 4 colors. The goal is to align all cubes so that each color is the same vertically. A tower with such an alignment is called tidy.
Two kinds of operations are allowed:
1. Rotate a cube: Rotate a single cube, and all cubes above it rotate as well.
2. Rotate with holding: Rotate a cube and hold a cube above it, preventing it and the cubes above it from rotating.
The cube colors are represented by the letters R, Y, B, and G, corresponding to red, yellow, blue, and green respectively. The forward-facing side of each cube is indicated by the first letter in the sequence. The color sequence is in clockwise order.

Here is an example:
I indicate the forward-facing side with R, Y, B, and G, corresponding to red, yellow, blue, and green respectively where the leftmost cube corresponds to the bottom cube (position 0): RGBYRGBYBGBGBG. Can you make this tower tidy in eight moves or less?
Solution for eight moves: RGBYRGBYBGBGBG → (rotate by one position at position 1 and not hold at position 2) RRGBYRGBGRGRGR → (rotate by one position at position 2 and hold at position 3) RRRBYRGBGRGRGR → (rotate by two positions at position 3 and hold at position 4) RRRRYRGBGRGRGR → (rotate by one at position 4 and hold at position 5) RRRRRRGBGRGRGR → (rotate by one at position 6 and hold at position 9) RRRRRRRGRRGRGR → (rotate by one at position 7 and hold at position 8) RRRRRRRRRRGRGR → (rotate by one at position 10 and hold at position 11) RRRRRRRRRRRRGR → (rotate by one at position 12 and hold at position 13) RRRRRRRRRRRRRR

Now, solve the puzzle to make the tower tidy: {tower}, the sides are arranged in clockwise order: R → Y → B → G.

The output format shoule strictly follow the following format:
Reasoning: Explain the logic used to solve the chosen cube, please remember that do not violate the rules of Tidy Tower.
Output: List[int]= [[Cube index, Rotation, Holding], [Cube index, Rotation, Holding], ...] cube index is the index of the cube to rotate. Index starts from 0 to {max_height}. 
Rotation is the clockwise rotation of the cube. Rotation is from 1 to 4, representing how many times the cube is rotated. The value of 1 means one clockwise rotation, 2 means two clockwise rotations, and so on. The value of 4 means four clockwise rotations, which is equivalent to no rotation. 'Hold or not' is a value of 0 or 1, representing whether to hold the cube above it or not.
'''

VOTE_PROMPT = '''This time you are provided several choices of answers. Please vote for the best one.'''

WITHOUT_HISTORY_PROMPT = '''Your task is to solve a puzzle named 'Tidy Tower'. You are given a tower consisting of {num_cubes} cubes, each of which has one of 4 colors. The goal is to align all cubes so that each color is the same vertically. A tower with such an alignment is called tidy.
Two kinds of operations are allowed:
1. Rotate a cube: Rotate a single cube, and all cubes above it rotate as well.
2. Rotate with holding: Rotate a cube and hold a cube above it, preventing it and the cubes above it from rotating.
The cube colors are represented by the letters R, Y, B, and G, corresponding to red, yellow, blue, and green respectively. The forward-facing side of each cube is indicated by the first letter in the sequence. The color sequence is in clockwise order.

For example, when the tower is represented as RGBYRGBYBGBGBG, and if I rotate cube index 1 and not hold the cube above it, the tower will be transformed to RRGBYRGBGRGRGR, but if I rotate cube index 1 and hold the cube above it, it will become RRBYRGBYBGBGBG.

The sides of the tower are arranged in clockwise order: R → Y → B → G. Please solve it iteratively and output one step at a time. For each step, you have to output a list containing three elements: the index of the cube to rotate, the number of clockwise rotations, and whether to hold the cube above it (1 for holding, 0 for not holding). The cube index starts from 0 to {max_height}. The rotation is from 1 to 4, representing how many times the cube is rotated. The value of 1 means one clockwise rotation, 2 means two clockwise rotations, and so on. The value of 4 means four clockwise rotations, which is equivalent to no rotation. 'Hold or not' is a value of 0 or 1, representing whether to hold the cube above it or not.

The output format shoule strictly follow the following format:
Reasoning: Explain the logic used to solve the chosen cube, please remember that do not violate the rules of Tidy Tower.
Operation: Specify one step in the format 'operation = [Cube index, Rotation, Holding]'.
Your previous operation was: {previous_operation}. Now, the tower is {tower}, please continue solving this puzzle by outputting your next operation.'''

LEGAL_CANDIDATES_PROMPT = '''To help you better making decision, you are provided a list of legal moves, which are some of the possible moves you can make, but they may not be the best ones. You can choose one of them or you can choose a move that is not in the list if you think it is better. Here is the list of legal moves: {legal_moves}.'''

PUZZLE_INTRO = '''Game Description
        
Game: Tidy Tower

Overview:
Tidy Tower is a puzzle game where you need to align all cubes so that each color is the same vertically. 
You can rotate a single cube, and all cubes above it rotate as well, or rotate a cube and hold a cube above it, preventing it and the cubes above it from rotating.

Mechanics:
1. Rotate a cube: Rotate a single cube, and all cubes above it rotate as well.
2. Rotate with holding: Rotate a cube and hold a cube above it, preventing it and the cubes above it from rotating.
'''