from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from abc import abstractmethod

from system.message import Info
from system.message import BaseMessageDataType
from model.strategy_type import StrategyType
from model.base import BaseStrategy

import random
import copy
from collections import Counter


class LargerTargetCustomStrategy:
    def __init__(self, model: BaseStrategy):
        self._model = model
        self.name = self._model.name
        self.history = self._model.history
        self.strategy_type = StrategyType.Custom
        self.bags = None
        self.index2bag = {}
        self.index_value = None
    
    def update_model_field(self, field_name: str, value: Any):
        if hasattr(self._model, field_name):
            setattr(self._model, field_name, value)

    def receive_message(self, message: Info) -> Info:  
        data = message.message[0].data

        self.index_value = [[] for _ in range(len(data['random_bag']))]

        if message.difficulty == 'easy':
            legal_bags = [i for i in range(len(data['random_bag'])) if i not in data['empty_bag']]
            selected_bag = random.choice(legal_bags)
            return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=selected_bag, type='custom')])
        elif message.difficulty == 'normal':
            if self.bags is None:
                self.bags = copy.deepcopy(data['random_bag'])

            if len(data['guess_bag']) == 0:
                selected_bag = random.randint(0, len(self.bags) - 1)
                return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=selected_bag, type='custom')])
            else:
                tmp_index_list = [-1]
                if len(data['guess_bag']) > 1:
                    tmp_index_list.append(-2)
                for index in tmp_index_list:
                    prev_index, prev_value = data['guess_bag'][index]
                    self.index_value[prev_index].append(prev_value)

                empty_bag = data['empty_bag'].copy()
                for idx in empty_bag:
                    if idx in self.index2bag:
                        continue
                    else:
                        for i in range(len(self.bags)):
                            if sorted(self.bags[i]) == sorted(self.index_value[idx]):
                                self.index2bag[idx] = i
                                break

                while True:
                    is_find = False
                    for i in range(len(data['random_bag'])):
                        if i in self.index2bag:
                            continue
                        candidate_bag = []
                        copy_bags = copy.deepcopy(self.bags)
                        for j in range(len(data['random_bag'])):
                            if j in self.index2bag.values():
                                continue
                            is_true_bag = True
                            for value in self.index_value[i]:
                                if value not in copy_bags[j]:
                                    is_true_bag = False
                                    break
                                else:
                                    copy_bags[j].remove(value)
                            if is_true_bag:
                                candidate_bag.append(j)
                        if len(candidate_bag) == 1:
                            self.index2bag[i] = candidate_bag[0]
                            is_find = True
                    if not is_find:
                        break
                
                # last bag mapping
                if len(self.index2bag) == len(data['random_bag'])-1:
                    for i in range(len(data['random_bag'])):
                        if i not in self.index2bag:
                            for j in range(len(data['random_bag'])):
                                if j not in self.index2bag.values():
                                    self.index2bag[i] = j
                                    break
                            break

                # deterministic max value
                deterministic_max = 0.0
                deterministic_index = 0
                for key, value in self.index2bag.items():
                    if key in empty_bag:
                        continue

                    counter1 = Counter(self.bags[value])
                    counter2 = Counter(self.index_value[key])
                    tmp_list = []
                    for item in counter1:
                        if counter1[item] > counter2[item]:
                            tmp_list.append(item)
                            counter1[item] -= 1
                    if len(tmp_list) == 0:
                        continue
                    tmp_value = sum(list(tmp_list)) / len(tmp_list)
                    if tmp_value > deterministic_max:
                        deterministic_max = tmp_value
                        deterministic_index = key

                # random max value
                tmp_bag = []
                random_max = 0.0
                for i in range(len(data['random_bag'])):
                    if i in self.index2bag.values() or i in empty_bag:
                        continue
                    tmp_bag.append(self.bags[i])

                random_max = 0.0
                mean_bag = [sum(bag) / len(bag) for bag in tmp_bag]
                if len(mean_bag) != 0:
                    random_max = sum(mean_bag) / len(mean_bag)
                if deterministic_max > random_max:
                    return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=deterministic_index, type='custom')])
                else:
                    tmp_list = [i for i in range(len(data['random_bag'])) if i not in empty_bag]
                    selected_bag = random.choice(tmp_list)
                    return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=selected_bag, type='custom')])
                

    