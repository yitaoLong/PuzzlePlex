from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from abc import abstractmethod

from system.message import Info
from system.message import BaseMessageDataType
from model.strategy_type import StrategyType
from model.base import BaseStrategy

import itertools
import random


class MaxMaximalCocktailsCustomStrategy:
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
        cnt_maximal_cocktails = data['cnt_maximal_cocktails']

        if message.difficulty == 'easy':
            existing_nodes = []

            for edge in edges_list:
                existing_nodes.append(edge[0])
                existing_nodes.append(edge[1])

            remaining_nodes = list(set(nodes_list) - set(existing_nodes))

            if len(remaining_nodes) >= 2:
                data = random.sample(remaining_nodes, 2)
                data = (data[0], data[1])
                return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=data, type='custom')])
            elif len(remaining_nodes) == 1:
                for node in nodes_list:
                    if node not in existing_nodes:
                        data = (node, remaining_nodes[0])
                        return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=data, type='custom')])
            else:
                data = None
                while True:
                    tmp = random.sample(nodes_list, 2)
                    if (tmp[0], tmp[1]) not in edges_list and (tmp[1], tmp[0]) not in edges_list:
                        data = (tmp[0], tmp[1])
                        break
                return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=data, type='custom')])
        elif message.difficulty == 'normal':
            matrix = [[0 for _ in range(len(nodes_list))] for _ in range(len(nodes_list))]
            for edge in edges_list:
                matrix[edge[0]-1][edge[1]-1] = 1
                matrix[edge[1]-1][edge[0]-1] = 1

            data = None
            for i in range(len(nodes_list)):
                for j in range(i+1, len(nodes_list)):
                    if matrix[i][j] == 0:
                        new_edges_list = edges_list.copy()
                        new_edges_list.append((i+1, j+1))
                        new_maximal_cocktails = self.calculate_num_maximal_cocktails(len(nodes_list), new_edges_list)
                        if new_maximal_cocktails >= cnt_maximal_cocktails:
                            data = (i+1, j+1)
                            break
                if data is not None:
                    break

            return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=data, type='custom')])
    
    def calculate_num_maximal_cocktails(self, num_nodes, edges_list):
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
        
        return len(maximal_cocktails)