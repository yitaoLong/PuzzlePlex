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


class ExclusivityParticlesCustomStrategy:
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
        dimension = data['dimension']
        distance = data['distance']
        cnt_particles = data['particles']
        if message.difficulty == 'easy':
            vector = [random.randint(0, 1) for _ in range(dimension)]
            count = 0
            while True:
                is_valid = True
                for particle in cnt_particles:
                    diff = 0
                    for i in range(dimension):
                        if particle[i] != vector[i]:
                            diff += 1
                    if diff < distance:
                        is_valid = False
                        break
                if is_valid:
                    break
                else:
                    count += 1
                    vector = [random.randint(0, 1) for _ in range(dimension)]
                    if count > 1000:
                        break
            return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=vector, type='custom')])
        elif message.difficulty == 'normal':
            vector = [random.randint(0, 1) for _ in range(dimension)]
            count = 0
            candidates = []
            while True:
                is_valid = True
                for particle in cnt_particles:
                    diff = 0
                    for i in range(dimension):
                        if particle[i] != vector[i]:
                            diff += 1
                    if diff < distance:
                        is_valid = False
                        break
                if is_valid:
                    candidates.append(vector)
                count += 1
                vector = [random.randint(0, 1) for _ in range(dimension)]
                if count > 1000:
                    break
            
            # select a candidate that may make the opponent lose
            return_vector = None
            for candidate in candidates:
                tmp_articles = copy.deepcopy(cnt_particles)
                tmp_articles.append(candidate)
                is_good = True
                vector = [random.randint(0, 1) for _ in range(dimension)]
                count = 0
                while True:
                    is_valid = True
                    for particle in tmp_articles:
                        diff = 0
                        for i in range(dimension):
                            if particle[i] != vector[i]:
                                diff += 1
                        if diff < distance:
                            is_valid = False
                            break
                    if is_valid:
                        is_good = False
                        break
                    else:
                        count += 1
                        vector = [random.randint(0, 1) for _ in range(dimension)]
                        if count > 1000:
                            break
                if is_good:
                    return_vector = candidate
                    break
            if return_vector is None:
                return_vector = random.choice(candidates)
            return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=return_vector, type='custom')])