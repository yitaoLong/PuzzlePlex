DESCRIPTION = '''As in many card games, particularly the game of War, each round involves each player choosing one card to play. Unlike other card games, each player can choose whether to compete with their card or to give it up. Points are calculated and accumulated after each round. At the end of the game, the player with the most points wins. A tie is possible, though unlikely. Now, let's go over the specific rules.

Rules:

- At the start of the game, each player is given a set of {num_cards} cards. Although the sets of cards may differ between players, the total value of the cards in each player's set is the same. The value of each card is equal to its numerical value, except for J, Q, K, and A, which have values of 11, 12, 13, and 1, respectively.

- In each round, each player chooses and confirms one card from their set to play. They then decide whether to compete with this card or to give it up. This process is private, meaning each player will not see the decision made by their opponent. Once a decision is made, the card is removed from the player's set, whether it was played or given up.

- After both players have made their decisions, points are calculated as follows:

1. If both players choose to compete, the player with the higher-value card wins and is awarded points equal to their card value plus their opponent's card value.
2. If both players choose to give up, neither player receives any points.
3. If player A chooses to compete and player B chooses to give up, then player A is awarded points equal to their card value, while player B receives no points.
- After both players have played all their cards, the player with the most points is the winner.
Provide your output in the following format:

Reasoning: ...

Operation: You must output a list containing the card you choose to play and whether you choose to compete or give up in the format `move = ['card', 'compete or give up']`. For example, if you choose to play the card '5' and compete, your output should be `move = ['5', 'compete']`. If you choose to play the card 'K' and give up, your output should be ` move = ['K', 'give up']`.\n'''

SIMPLIFIED_DESCRIPTION = None

STATE_TRANSIT_PROMPT = None

CODE_PROMPT = '''You are about to play a game called **Beat or Bomb Sto** against an opponent.

Rules
-----
1. At the start of the game, each player is given a set of cards. Although the sets of cards may differ between players, the **total value** of the cards for each player is the same.
2. Card values are assigned as follows:
   - Numbered cards are worth their number (e.g., '2' is 2 points).
   - Face cards have special values: 'J' = 11, 'Q' = 12, 'K' = 13, and 'A' = 1.
3. In each round:
   - You select one card from your remaining cards.
   - You privately choose whether to **compete** with that card or **give it up**.
   - Regardless of your choice, the selected card is removed from your set.
4. After both players have made their decisions, scoring happens:
   - If **both players compete**, the higher card wins and gains points equal to (own card value + opponent's card value).
   - If **both players give up**, no points are awarded.
   - If **one competes and one gives up**, the competitor earns points equal to their card's value, while the giver-upper gets 0.
5. After all cards have been played, the player with the highest total score wins. A tie is possible.

Example
--------
Suppose your hand is `['2', '5', 'K']`, and your opponent also has a different set but the total value is the same.  
- First round, you choose '5' and decide to **compete**.
- Your opponent plays '3' and **gives up**.
- You earn 5 points, your opponent earns 0.

Task
----
Implement a Python strategy that, given your current `my_remaining_cards`, `my_current_score`, and `opponent_current_score`, returns the best **card and operation** to choose for this round.

**Input Format:**  
- `my_remaining_cards`: a list of strings, each being a card from `'A'`, `'2'` to `'10'`, `'J'`, `'Q'`, `'K'`.
- `my_current_score`: an integer representing your current points.
- `opponent_current_score`: an integer representing your opponent's points.
- `my_prev_decision`: a tuple of strings, where the first string is the card you played in the previous round and the second string is either `'compete'` or `'give up'`.
- `opponent_prev_decision`: a tuple of strings, where the first string is the card your opponent played in the previous round and the second string is either `'compete'` or `'give up'`.

**Output Format:**  
- Return a list in the format `[card, operation]`, where `card` is a string and `operation` is either `'compete'` or `'give up'`.

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

class BeatOrBombStoCustomStrategy:
    def __init__(self, model: BaseStrategy):
        self._model = model
        self.name = self._model.name
        self.history = self._model.history
        self.strategy_type = StrategyType.Custom
    
    def update_model_field(self, field_name: str, value: Any):
        if hasattr(self._model, field_name):
            setattr(self._model, field_name, value)

    def receive_message(self, message: Info) -> Info: 
        # my remaining cards is a list of str, where str from 'A', '2' to '10', 'J', 'Q', 'K'
        my_remaining_cards = message.message[0].data[0]
        # an integer indicates my current score
        my_current_score = message.message[0].data[1]
        # an integer indicates my opponent score
        opponent_current_score = message.message[0].data[2]
        # a tuple of str, where str is the card I played in the previous round and the second str is either 'compete' or 'give up', None if no previous round
        my_prev_decision = message.message[0].data[3]
        # a tuple of str, where str is the card my opponent played in the previous round and the second str is either 'compete' or 'give up', None if no previous round
        opponent_prev_decision = message.message[0].data[4]
        
        chosen_move = None
        # TODO: implement your decision logic here

        return Info(
            sender=self.__class__.__name__,
            receiver=message.sender,
            difficulty=message.difficulty,
            message=[BaseMessageDataType(data=chosen_move, type='custom')]
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

* `reasoning` — concise explanation describing how you selected the `chosen_move`.
* `code` — complete, syntax-error-free Python implementing the decision logic, with **no** ```python fences or other formatting.
'''

PUZZLE_INTRO = '''Game Description
        
Game: Beat or Bomb (Stochastic)
        
Overview:
In this strategic card game, two players are each given a set of cards with the same total value but potentially different individual cards. The game is played over several rounds, where each player chooses a card to play and decides whether to compete with it or give it up. The objective is to accumulate the most points by the end of the game.

Mechanics:
1. Card Values: Each card has a numerical value, with special values assigned to J, Q, K, and A (11, 12, 13, and 1, respectively).

2. Rounds: In each round, both players secretly choose one card to play and decide whether to compete or give up. Once decisions are made, the cards are revealed and points are awarded based on the following:
- If both players choose to compete, the player with the higher-value card wins and receives points equal to their card value plus their opponent's card value.
- If both players choose to give up, neither player gains points.
- If one player competes and the other gives up, the competing player receives points equal to their card value.

3. Winning: The player with the most points at the end of all rounds wins the game.'''