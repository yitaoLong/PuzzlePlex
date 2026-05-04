DESCRIPTION = '''You are playing a game with {num_boxes} covered boxes of Burmese rubies in front of you.
You are told that there are exactly {total_rubies} identical seven-carat rubies in total across the boxes, but you don't know how many rubies are inside each individual box.
Each turn, you can make a request for a number of rubies from each box.
If your request for a box is less than or equal to the number of rubies inside that box, you successfully receive the requested amount from that box.
If your request exceeds the number of rubies in the box, you receive nothing from that box.
You proceed box by box in the given order.

For example, suppose there are 3 boxes, and the hidden rubies in each box are: [11, 9, 10].
Total rubies = 30.
Turn 1:
You request 10 rubies.
Feedback: 10 (successfully take 10 rubies).
Turn 2:
You request 8 rubies.
Feedback: 8 (successfully take 8 rubies).
Turn 3:
You request 12 rubies.
Feedback: 0 (because 12 > 10, so you get nothing from that box).
Total rubies collected so far: 18.

Now it is turn {turn}, please decide how many rubies you want to request this turn.
Provide the output in the following format:
Reasoning: Explain your reasoning clearly — why your choice is good based on previous feedback and your current goal.
Operation: Output your request for this turn using this format: 'List[int] = [number of rubies you request for this turn]'
'''

SIMPLIFIED_DESCRIPTION = None

STATE_TRANSIT_PROMPT = '''It is now Turn {turn}. You received {rubies} rubies from the last box you requested. Please decide your request for the next box.
Your request must be in the following format: Operation: Output the request in the format: 'List[int]' = [the number of rubies you request this turn]
'''

CODE_PROMPT = '''You are about to play a game called **Ruby Risks**.

Rules
-----
1. You are presented with a set of covered boxes containing Burmese rubies.
2. You are told the **total number** of rubies across all boxes, but **not** the individual counts per box.
3. Each turn, you **request a number of rubies**.
4. For each box, if your request is **less than or equal to** the number of rubies inside, you successfully collect that many rubies from the box.
5. If your request is **more than** the rubies in the box, you collect **nothing** from that box.
6. The boxes are processed **in order**, one after another.
7. Your goal is to **maximize the number of rubies collected** across turns.

Example  
--------
Suppose there are 3 boxes with hidden rubies: [11, 9, 10].  
Total rubies = 30.

- Turn 1:  
  Request: 10 rubies  
  Feedback: 10 (successfully took 10 rubies from the first box).

- Turn 2:  
  Request: 8 rubies  
  Feedback: 8 (successfully took 8 rubies from the second box).

- Turn 3:  
  Request: 12 rubies  
  Feedback: 0 (because 12 > 10, so no rubies collected from the third box).

Total collected so far: 18 rubies.

Task
----
Implement a Python strategy that, given the current `total_rubies`, `current_turn`, `feedback`, and `boxes`, decides how many rubies to request for this turn.

**Input Format:**  
- `total_rubies`: an integer representing the total number of rubies across all boxes.  
- `current_turn`: an integer representing the current turn number (starting from 1).  
- `feedback`: a list of integers representing how many rubies you successfully collected at each previous turn.  
- `boxes`: an integer representing the total number of boxes.

**Output Format:**  
- Return an integer representing the number of rubies you request for this turn.

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

class RubyRisksCustomStrategy:  
    def __init__(self, model: BaseStrategy):  
        self._model = model  
        self.name = self._model.name  
        self.history = self._model.history  
        self.strategy_type = StrategyType.Custom  

    def update_model_field(self, field_name: str, value: Any):  
        if hasattr(self._model, field_name):  
            setattr(self._model, field_name, value)  

    def receive_message(self, message: Info) -> Info:  
        data = message.message[0].data  
        # total_rubies: int, current_turn: int, feedback: List[int], boxes: int  
        total_rubies, current_turn, feedback, boxes = data  
        rubies_requested = None  
        # TODO: implement your decision logic here
        return Info(  
            sender=self.__class__.__name__,  
            receiver=message.sender,  
            difficulty=message.difficulty,  
            message=[BaseMessageDataType(data=rubies_requested, type='custom')]  
        )

Guidelines
----------
* The existing template should not be modified. You can **add helper functions, variables, or classes** as needed.
* You can import additional libraries if needed. Assume all libraries are pre-installed.

Required Output Format
----------------------
Return a single JSON object:

{
  "reasoning": "<your step-by-step explanation>",
  "code": "<only the Python code and the code must be complete including the template>"
}

- `reasoning` — Provide a **concise explanation** of how you determine the number of rubies to request based on total, previous feedback, and strategic considerations.
* `code` — complete, syntax-error-free Python implementing the decision logic, with **no** ```python fences or other formatting.
'''

PUZZLE_INTRO = '''Game Description
        
Game: Ruby Risks
        
Overview:
In this game, you have several covered boxes of Burmese rubies before you. You know there are a total of fixed identical seven-carat rubies in the several boxes. You can ask for a certain number of rubies from each box. If you ask for more than there are, you get none from that box. Otherwise, you get what you asked for from that box.

Mechanics:
1. Objective:
- Player can make a request for the number of rubies from each box.
- Based on the feedback, player can make a request for the next box.
- Player can make a request for the next box until the game ends.

2. Game End:
- The game ends when the player has made a request for all the boxes.
- The player with the highest score will win the game.

3. Scoring:
- The score is the sum of the number of rubies you get from the the  boxes.'''