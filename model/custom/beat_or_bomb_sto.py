from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from abc import abstractmethod

from system.message import Info
from system.message import BaseMessageDataType
from model.strategy_type import StrategyType
from model.base import BaseStrategy

import random


class BeatOrBombStoCustomStrategy:
    def __init__(self, model: BaseStrategy):
        self._model = model
        self.name = self._model.name
        self.history = self._model.history
        self.strategy_type = StrategyType.Custom
        self.my_remaining_cards = None
        self.opponent_remaining_cards = None
        self.my_current_score = 0
        self.opponent_current_score = 0
        self.score_dict = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13}
        self.total_score = None
        self.opponent_max_remaining_score = None
        self.my_moves = []
        self.opponent_moves = []
    
    def update_model_field(self, field_name: str, value: Any):
        if hasattr(self._model, field_name):
            setattr(self._model, field_name, value)

    def receive_message(self, message: Info) -> Info: 
        self.my_remaining_cards = message.message[0].data[0]
        self.my_current_score = message.message[0].data[1]
        self.opponent_current_score = message.message[0].data[2]

        if self.total_score is None:
            self.total_score = 0
            for c in self.my_remaining_cards:
                self.total_score += self.score_dict[c]
            self.opponent_max_remaining_score = self.total_score
        
        my_last_move = message.message[0].data[3]
        opponent_last_move = message.message[0].data[4]

        if opponent_last_move is not None:
            self.opponent_moves.append(opponent_last_move)
            self.opponent_max_remaining_score -= self.score_dict[opponent_last_move[0]]
        if my_last_move is not None:
            self.my_moves.append(my_last_move)

        if message.difficulty == 'easy':
            card = random.choice(self.my_remaining_cards)
            data = [card, 'compete']
            return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=data, type='custom')])
        elif message.difficulty == 'normal':            
            # Strategy implementation
            card, move = self.choose_move()
            
            data = [card, move]
            return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=data, type='custom')])

    def choose_move(self):
        # Strategy 1: If we're ahead and can't be caught, give up remaining cards
        if self.my_current_score > self.opponent_current_score + self.opponent_max_remaining_score:
            return random.choice(self.my_remaining_cards), 'give up'

        # Strategy 2: If it's the last round, compete with the highest card
        if len(self.my_remaining_cards) == 1:
            return self.my_remaining_cards[0], 'compete'

        # Strategy 3: Compete with high cards, give up low cards
        highest_card = max(self.my_remaining_cards, key=lambda x: self.score_dict[x])
        lowest_card = min(self.my_remaining_cards, key=lambda x: self.score_dict[x])

        if self.score_dict[highest_card] > 10:
            return highest_card, 'compete'
        elif self.score_dict[lowest_card] < 5:
            return lowest_card, 'give up'

        # Strategy 4: Choose a card based on opponent's likely cards
        opponent_played_cards = [move[0] for move in self.opponent_moves]
        opponent_likely_cards = [card for card in self.score_dict.keys() if card not in opponent_played_cards]
        average_opponent_card_value = sum(self.score_dict[card] for card in opponent_likely_cards) / len(opponent_likely_cards)
        
        for card in sorted(self.my_remaining_cards, key=lambda x: self.score_dict[x], reverse=True):
            if self.score_dict[card] > average_opponent_card_value:
                return card, 'compete'

        # Strategy 5: Play conservatively if behind
        if self.my_current_score < self.opponent_current_score:
            return max(self.my_remaining_cards, key=lambda x: self.score_dict[x]), 'compete'

        # Default strategy: Compete with a mid-value card
        mid_value_cards = sorted(self.my_remaining_cards, key=lambda x: abs(self.score_dict[x] - 7))
        return mid_value_cards[0], 'compete'