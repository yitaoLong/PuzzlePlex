from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from abc import abstractmethod

from system.message import Info
from system.message import BaseMessageDataType
from model.strategy_type import StrategyType
from model.base import BaseStrategy

import random


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
        difficulty = message.difficulty
        if difficulty == 'easy':
            chosen_card = random.choice(cards)
        else:
            chosen_card = self.find_best_move(cards, stones)

        return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=chosen_card, type='custom')])

    def can_win_dp(self, cards, stones):
        # Initialize the DP table
        dp = [False] * (stones + 1)
        dp[0] = True  # Base case: 0 stones is a winning position

        # Fill the DP table
        for i in range(1, stones + 1):
            for card in cards:
                if card <= i and not dp[i - card]:
                    dp[i] = True
                    break

        return dp[stones]

    def find_best_move(self, cards, stones):
        best_move = None
        for card in cards:
            if card <= stones:
                new_cards = cards.copy()
                new_cards.remove(card)
                new_stones = stones - card
                
                if not self.can_win_dp(new_cards, new_stones):
                    return card  # This move leads to a winning position
        
        # If no winning move is found, choose the move that leaves the opponent
        # with the least chance of winning
        for card in cards:
            if card <= stones:
                new_cards = cards.copy()
                new_cards.remove(card)
                new_stones = stones - card
                
                if not self.can_win_dp(new_cards, new_stones):
                    best_move = card
                    break
        
        # If all moves lead to a loss, choose the largest card
        return best_move if best_move is not None else max(card for card in cards if card <= stones)
