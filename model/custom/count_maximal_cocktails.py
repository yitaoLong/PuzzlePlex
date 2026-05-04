from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from abc import abstractmethod

from system.message import Info
from system.message import BaseMessageDataType
from model.strategy_type import StrategyType
from model.base import BaseStrategy


class CountMaximalCocktailsCustomStrategy:
    def __init__(self, model: BaseStrategy):
        self._model = model
        self.name = self._model.name
        self.history = self._model.history
        self.strategy_type = StrategyType.SMT
    
    def update_model_field(self, field_name: str, value: Any):
        if hasattr(self._model, field_name):
            setattr(self._model, field_name, value)

    def receive_message(self, message: Info) -> Info:
        data = message.message[0].data

        nodes_list = data['nodes']
        edges_list = data['edges']
        num_nodes = len(nodes_list)

        # find all maximal cocktails
        all_possible = []
        for i in range(1 << num_nodes):
            subset = []
            for j in range(num_nodes):
                if i & (1 << j):
                    subset.append(j+1)
            is_maximal = True
            for cocktail in all_possible:
                if set(subset).issubset(set(cocktail)):
                    is_maximal = False
                    break
            if is_maximal:
                all_possible.append(subset)

        maximal_cocktails = {}
        for i in range(len(all_possible)-1, -1, -1):
            is_good = True
            for j in range(len(edges_list)):
                e1, e2 = edges_list[j]
                if e1 in all_possible[i] and e2 in all_possible[i]:
                    is_good = False
                    break
            if is_good:
                if len(all_possible[i]) not in maximal_cocktails:
                    maximal_cocktails[len(all_possible[i])] = [set(all_possible[i])]
                else:
                    maximal_cocktails[len(all_possible[i])].append(set(all_possible[i]))

        # select the maximal cocktails with the largest size
        maximal_cocktails = maximal_cocktails[max(maximal_cocktails.keys())]
        
        if message.difficulty == 'easy':
            return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=len(maximal_cocktails), type='custom')])
        elif message.difficulty == 'normal':
            return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=maximal_cocktails, type='custom')])