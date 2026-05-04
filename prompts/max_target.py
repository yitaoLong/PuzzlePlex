DESCRIPTION = '''You have {bag_count} bags, each containing multiple coins with different values. Your goal is to maximize the total sum of coin values you collect by strategically choosing bags.
Before the game starts, you'll be informed of:

1. The coin values inside each bag
2. The total number of picks you can make

However, the actual order of the bags will be randomized. On each turn, you'll select a bag index, and a coin will be randomly drawn from that bag. For example, if you're told the bags contain [1, 2] and [2, 3], but the actual order is [[2, 3], [1, 2]], selecting bag index 0 will give you a random coin value from [2, 3].
To maximize your score, you'll need to carefully consider the coin values in each bag and the number of remaining picks.
For example, if you're told the bags contain [1, 2] and [3, 4], and the total number of picks is 2. If you pick bag 0 and get a coin value of 4, then in the next turn, you will know that bag 0 contains [3, 4] and bag 1 contains [1, 2], and value 4 in bag 0 is removed and remaining values are [3]. So, if you pick bag 0 again, you will get a coin value of 3, which is bigger than the coin value of bag 1. So, you should pick bag 0 again to maximize your score.
Provide the output in the following format:
Reasoning: ...
Operation: Output the index of the bag you want to pick from (0-indexed) in the format `bag_index = [x]`, where x is the index of the bag you want to pick from. You must output a specific index in int, if you do not know how to choose, please randomly choose a bag index in the format `bag_index = [int]`. Otherwise, you will lose the game.
Among all the bags, the coin values are {bag_coins}. You have {max_guess} picks in total. Please make your first pick.
'''

SIMPLIFIED_DESCRIPTION = None

STATE_TRANSIT_PROMPT = None

CODE_PROMPT = '''You are about to play a game called **Max Target**.

Rules
-----
1. You have several bags, each containing multiple coins with different values.
2. Before the game starts, you are informed of the contents of each bag.
3. However, the **actual order** of the bags will be **randomized** during gameplay.
4. On each turn, you **select a bag index**, and **one coin will be randomly drawn** from that bag.
5. After a coin is drawn, it is removed from the bag.
6. Your goal is to **maximize the total sum of coin values you collect** over all your picks.
7. You have a **fixed number of picks** in total.
8. If a bag becomes empty, it cannot be picked again.

Example  
--------
Suppose you are told that the bags contain:  
Bag 0: [1, 2]  
Bag 1: [3, 4]  

But the actual randomized bags are:  
Bag 0: [3, 4]  
Bag 1: [1, 2]  

If you pick bag 0 and draw a 4, the updated bag contents become:  
Bag 0: [3]  
Bag 1: [1, 2]  

At this point, it's better to **pick bag 0 again** because 3 is larger than the possible outcomes from bag 1.

Task
----
Implement a Python strategy that, given the current `random_bag`, `guess_bag`, `value_received`, `empty_bag`, and `max_guess`, returns the best `bag_index` to pick from.

**Input Format:**  
- `random_bag`: a list of lists of integers, representing the current coins in each randomized bag.  
- `guess_bag`: a list of tuples (bag index, value drawn), representing your previous picks and outcomes.  
- `value_received`: an integer representing your cumulative score so far.  
- `empty_bag`: a list of integers representing indices of bags that have become empty.  
- `max_guess`: an integer representing the total number of picks you are allowed.

**Output Format:**  
- Return an integer representing the bag index you want to pick from (0-indexed).  

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

class MaxTargetCustomStrategy:
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
        #   'value_received': int,             # your received score
        #   'empty_bag': List[int],             # list of empty bag indexes
        #   'max_guess': int                   # the number of guesses you can make
        # }
        data = message.message[0].data
        # return index of bag
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
* The existing template should not be modified. You can add variables, functions, or classes as needed.
* You can import additional libraries and assume they are already installed.  

Required Output Format
----------------------
Return a single JSON object:

{
  "reasoning": "<your step-by-step explanation>",
  "code": "<only the Python code and the code must be complete that including code in template>"
}

* `reasoning` — concise explanation of how you determined `chosen_bag`.
* `code` — complete, syntax-error-free Python implementing the decision logic, with **no** ```python fences or other formatting.
'''

PUZZLE_INTRO = '''Game Description
        
Game: Max Target
        
Overview:
Maximize Coin Value is a single-player puzzle game where you aim to collect the highest total coin value from a set of four bags, each containing coins of different values. Before the game begins, you will know the coin values in each bag, but the order of the bags will be randomized. On each turn, you will select a bag, and a coin will be randomly drawn from it. Your objective is to strategically select bags to maximize your total score.

Mechanics:
1. Bag Configuration:
- Bags: There are four bags, each containing multiple coins with varying values.
- Coin Values: The coin values inside each bag are revealed before the game, but the actual order of the bags is randomized.

2. Objective:
- On each turn, you select a bag index, and a random coin is drawn from that bag.
- The goal is to maximize the sum of coin values you collect by making the best choices with the information available.

3. Conditions:
- The total number of picks you can make is predetermined.
- Once a coin is drawn from a bag, it is removed, affecting the future value of that bag.
- The game continues until all your picks are made, and your score is the sum of the coin values you've collected.'''