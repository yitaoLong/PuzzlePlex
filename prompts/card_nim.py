DESCRIPTION = '''You are about to play a game called Card Nim against an opponent. The rules are as follows:
Each player starts with a hand of cards, each card showing a number. The game begins with a pile of stones. On each turn, a player must play one card to remove that many stones from the pile. A card can only be played if its number is less than or equal to the current number of stones. The player who removes the last stone wins. However, if a player cannot make a legal move (i.e., all their cards are greater than the number of remaining stones), he loses.

For example, if there are 5 stones, and both players have the same three cards: [1, 2, 3]. You go first. Who wins?
Your opponent wins. Because if you removes 2 or 3, then opponent can win immediately with 3 or 2 respectively. So, you removes 1. Now your opponent removes 3, leaving 1. Now you has only cards with numbers greater than 1 so you lose.

Now you and your oppnent have the same list of cards: {cards}. The number of stones is {stones}.

Provide your output in the following format:

Reasoning: Explain your reasoning of playing the card.

Operation: Output the card you choose to play in the format `List[int]`: [card].
'''

SIMPLIFIED_DESCRIPTION = None

STATE_TRANSIT_PROMPT = '''Your opponent played the card {card_played} and there are {stones} stones left. You have the following cards: {your_cards}. Please make your move in the format of `List[int]`: [card to play].'''

CODE_PROMPT = '''You are about to play a game called **Card Nim** against an opponent.

Rules
-----
1. The game starts with a pile of stones.
2. Each player has a hand of cards, each showing a positive integer.
3. On your turn you must play exactly one card and remove that many stones.
4. A card is playable only if its number ≤ current stones.
5. Whoever removes the **last stone wins**.
6. If you have **no playable card** (all remaining cards > current stones), you lose immediately.

Example  
--------
Stones = 5, hands = [1, 2, 3] for both players. You move first.  
• Play 2 → opponent plays 3 → 0 stones → you lose.  
• Play 3 → opponent plays 2 → 0 stones → you lose.  
So your best try is to play 1. Opponent then plays 3 (stones = 1). Your remaining cards (2, 3) are unplayable, so you lose.

Task
----
Implement a Python strategy that, given the current `cards`, `stones`, and `opponent_card_played`, returns the best card to play next.

**Input Format:**  
- `cards`: a list of integers, representing your remaining cards.  
- `stones`: an integer representing the current number of stones.  
- `opponent_card_played`: an integer representing the card your opponent just played.

**Output Format:**  
- Return an integer representing the card you choose to play.  

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

class CardNimCustomStrategy:
    def __init__(self, model: BaseStrategy):
        self._model = model
        self.name = self._model.name
        self.history = self._model.history
        self.strategy_type = StrategyType.Custom
    
    def update_model_field(self, field_name: str, value: Any):
        if hasattr(self._model, field_name):
            setattr(self._model, field_name, value)
            
    def receive_message(self, message: Info) -> Info:
        cards, stones, opponent_card_played = message.message[0].data
        chosen_card = None
        # TODO: implement your decision logic here
        return Info(
            sender=self.__class__.__name__,
            receiver=message.sender,
            difficulty=message.difficulty,
            message=[BaseMessageDataType(data=chosen_card, type='custom')]
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

* `reasoning` — concise explanation of how you determined `chosen_card`.
* `code` — complete, syntax-error-free Python implementing the decision logic, with **no** ```python fences or other formatting.
'''

PUZZLE_INTRO = '''Game Description
        
Game: Card Nim
        
Overview:
Card Nim is a two-player game where players take turns playing cards from their hand. Each card has a number on it, and the player who plays the card with the number equal to the remaining stones wins the game. The player who plays the card with a number greater than the remaining stones loses. 

Mechanics:

1. Initial Setup: The game starts with a number of stones placed in the center of the table. This number is randomly determined by the game generator.

2. Card Distribution: Each player is initially dealt a set of cards. 

3. Game Play:

    a. Player 1 (Left) starts the game by playing a card. The number of stones removed by this card is equal to the number on the card played.
    b. Player 2 (Right) then plays a card. The number of stones removed by this card is equal to the number on the card played.
    c. The game continues in this manner, with each player alternating turns until all cards are played or the game is won.

4. Winning Condition: A player wins the game if they play a card whose number is equal to the remaining number of stones. The game ends when all stones are removed or when a player wins.

5. Scoring: The winner of the game is the player who plays the last card that wins the game. The loser of the game is the player who plays the last card that does not win the game.'''