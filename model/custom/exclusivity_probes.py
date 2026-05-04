from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from abc import abstractmethod

from system.message import Info
from system.message import BaseMessageDataType
from model.strategy_type import StrategyType
from model.base import BaseStrategy

import random


class ExclusivityProbesCustomStrategy:
    def __init__(self, model: BaseStrategy):
        self._model = model
        self.name = self._model.name
        self.history = self._model.history
        self.strategy_type = StrategyType.Custom
        self.true_vector = []
        self.guess_vector = []
    
    def update_model_field(self, field_name: str, value: Any):
        if hasattr(self._model, field_name):
            setattr(self._model, field_name, value)

    def receive_message(self, message: Info) -> Info:
        data = message.message[0].data
        dimension = data['dimension']
        num_particles = data['num_particles']
        distance = data['distance']
        prev_guess = data['guess']
        is_particle = data['is_particle']

        if is_particle:
            self.true_vector.append(prev_guess)

        if len(self.true_vector) == 0:
            # random guess
            while True:
                g = [random.randint(0, 1) for _ in range(dimension)]
                if g not in self.guess_vector:
                    self.guess_vector.append(g)
                    break
            return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=g, type='custom')])
        else:
            response = self.generate_vectors(dimension, distance)
            self.guess_vector.append(response)
            return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=response, type='custom')])

    def generate_vectors(self, d, k):
        return_vector = None
        valid_vector_found = False
        while not valid_vector_found:
            # Start with a copy of one of the existing vectors
            candidate_vector = random.choice(self.true_vector)[:]

            # Flip at least k bits to ensure the distance condition
            flipped_bits = set()
            while len(flipped_bits) < k:
                bit_index = random.randint(0, d - 1)
                if bit_index not in flipped_bits:
                    flipped_bits.add(bit_index)
                    candidate_vector[bit_index] = 1 - candidate_vector[bit_index]

            # Check if the candidate vector satisfies the distance condition
            valid = True
            for vector in self.true_vector:
                hamming_distance = sum(a != b for a, b in zip(candidate_vector, vector))
                if hamming_distance < k:
                    valid = False
                    break

            if candidate_vector in self.guess_vector:
                valid = False

            if valid:
                return_vector = candidate_vector
                valid_vector_found = True

        return return_vector