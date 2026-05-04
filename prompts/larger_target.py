DESCRIPTION = '''You need to play a puzzle name 'target' against another player. In this game, there are {bag_count} bags, each containing multiple coins with different values. Two players take turns picking coins from a selection of bags. Your goal is to get a higher total sum of coin values than your opponent by strategically choosing bags.
Before the game starts, you'll be informed of:

1. The coin values inside each bag
2. The total number of picks you and your opponent can make

However, the actual order of the bags will be randomized. On each turn, you'll select a bag index, and a coin will be randomly drawn from that bag. For example, if you're told the bags contain [1, 2] and [2, 3], but the actual order is [[2, 3], [1, 2]], selecting bag index 0 will give you a random coin value from [2, 3].
To make your score higher than your opponent, you'll need to carefully consider the coin values in each bag and the number of remaining picks.
For example, if you're told the bags contain [1, 2] and [3, 4], and the total number of picks is 2. If your opponent pick bag 0 and get a coin value of 3, then in your turn, you will know that bag 0 contains [3, 4] and bag 1 contains [1, 2], and value 3 in bag 0 is removed and remaining values are [4]. So, if you pick bag 0 again, you will get a coin value of 4, which is bigger than the coin value of bag 1. So, you should pick bag 0 to make your score higher than your opponent.
Provide the output in the following format:
Reasoning: ...
Operation: Output the index of the bag you want to pick from (0-indexed) in the format of a list `bag_index = [x]`, where x is the index of the bag you want to pick from. You must output a specific index in int, if you do not know how to choose, please randomly choose a bag index in the format `bag_index = [int]`. Otherwise, you will lose the game.
Among all the bags, the coin values are {bag_coins}. And you and your opponent can make {max_guess} picks in total.\n'''

SIMPLIFIED_DESCRIPTION = None

STATE_TRANSIT_PROMPT = None

CODE_PROMPT = '''You are about to play a game called **Target** against an opponent.

Rules
-----
1. There are several bags, each containing multiple coins with different values.
2. The order of the bags is randomized at the start of the game.
3. On each turn, you select a bag index, and a coin is randomly drawn from that bag.
4. The goal is to collect a **higher total sum** of coin values than your opponent after all picks are completed.
5. You and your opponent picks, alternating turns.

Important Details
-----------------
- Before the game begins, you know the coin values inside each bag (but not the randomized order).
- After each move, you will know:
  - Which bag index was chosen.
  - What coin value was drawn from it.
  - Which bags have become empty.
- After a coin is drawn, it is removed from its bag.

Example  
--------
Suppose:
- Coin bags are: `[[1, 2], [3, 4]]`
- Randomized order becomes: `[[3, 4], [1, 2]]`
- Total picks: 2 per player.

If your opponent picks bag 0 and draws 3:
- You observe bag 0 has remaining coins `[4]`, and bag 1 has `[1, 2]`.
- To maximize your score, you should pick bag 0 to get the 4 (rather than risk picking from bag 1).

Task
----
Implement a Python strategy that, given the current `random_bag`, `guess_bag`, `your_received_value`, `opponent_received_value`, and `empty_bag`, decides which bag index to pick next.

**Input Format:**  
- `random_bag`: list of lists of integers, representing the current coins in each bag.
- `guess_bag`: list of tuples `(bag_index, coin_value)`, representing history of all previous picks.
- `your_received_value`: integer representing your current total.
- `opponent_received_value`: integer representing your opponent's current total.
- `empty_bag`: list of integers representing the indexes of bags that are now empty.

**Output Format:**  
- Return an integer representing the bag index you choose to pick from (0-indexed).

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

class LargerTargetCustomStrategy:
    def __init__(self, model: BaseStrategy):
        self._model = model
        self.name = self._model.name
        self.history = self._model.history
        self.strategy_type = StrategyType.Custom
    
    def update_model_field(self, field_name: str, value: Any):
        if hasattr(self._model, field_name):
            setattr(self._model, field_name, value)

    def receive_message(self, message: Info) -> Info:  
        # The data is a dict:
        # {
        #   'random_bag': List[List[int]],    # coin values in each bag
        #   'guess_bag': List[Tuple[int,int]], # past move history (bag index, value drawn)
        #   'your_received_value': int,        # your current score
        #   'opponent_received_value': int,    # opponent's current score
        #   'empty_bag': List[int]              # list of empty bag indexes
        # }
        data = message.message[0].data
        chosen_bag = None
        # TODO: implement your decision logic here
        return Info(
            sender=self.__class__.__name__,
            receiver=message.sender,
            difficulty=message.difficulty,
            message=[BaseMessageDataType(data=chosen_bag, type='custom')]
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

* `reasoning` — concise explanation of how you decided which bag to pick.
* `code` — complete, syntax-error-free Python implementing the decision logic, with **no** ```python fences or other formatting.
'''

PUZZLE_INTRO = '''Game Description
        
Game: Larger Target
        
Overview:
Larger Target is a two-player game where players take turns selecting coins from a set of four bags, each containing coins of different values. The goal is to accumulate a higher total sum of coin values than your opponent by strategically choosing from the bags. Players are informed of the coin values in each bag before the game starts, but the order of the bags is randomized.

Mechanics:
1. Bag Configuration:
- Bags: There are four bags, each containing multiple coins with predetermined values.
- Coin Values: The coin values inside each bag are known to both players before the game begins, but the bags' order is randomized.

2. Objective:
- Players take turns selecting a bag index and randomly drawing a coin from the selected bag.
- The aim is to maximize the sum of your coin values while outscoring your opponent by carefully choosing the bag that offers the best potential outcome.

3. Conditions:
- The total number of picks each player can make is predefined.
- After a coin is drawn from a bag, it is removed, altering the bag's remaining value.
- The game continues until all picks have been made, and the player with the higher total sum of coin values wins.'''