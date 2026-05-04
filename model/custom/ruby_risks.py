from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from abc import abstractmethod

from system.message import Info
from system.message import BaseMessageDataType
from model.strategy_type import StrategyType
from model.base import BaseStrategy

import random
from collections import Counter

class RubyRisksCustomStrategy:
    def __init__(self, model: BaseStrategy):
        self._model = model
        self.name = self._model.name
        self.history = self._model.history
        self.strategy_type = StrategyType.Custom
        self.samples = None
        self.previous_requests = []
        self.num_samples = 100000  # Large number for accuracy

    def generate_sample(self, n, S):
        r = [0] * n
        for _ in range(S):
            box = random.randint(0, n-1)
            r[box] += 1
        return r

    def update_model_field(self, field_name: str, value: Any):
        if hasattr(self._model, field_name):
            setattr(self._model, field_name, value)

    def receive_message(self, message: Info) -> Info:
        data = message.message[0].data
        total_rubies, current_turn, feedback, boxes = data
        n = boxes
        S = total_rubies
        k = current_turn

        if k == 1:
            self.samples = [self.generate_sample(n, S) for _ in range(self.num_samples)]
            self.previous_requests = []
        else:
            # Filter samples based on the last feedback
            j = k - 2  # Index for the last turn
            fj = feedback[j]
            qj = self.previous_requests[j]
            if fj == qj:
                self.samples = [r for r in self.samples if r[j] >= qj]
            else:
                self.samples = [r for r in self.samples if r[j] < qj]

        # Now, self.samples are filtered up to turn k-1
        if not self.samples:
            rubies_requested = 1
        else:
            rk_values = [r[k-1] for r in self.samples]
            if not rk_values:
                rubies_requested = 1
            else:
                counter = Counter(rk_values)
                max_rk = max(counter.keys()) if counter else 0
                cumulative = 0
                best_q = 1
                best_value = 0
                total_samples = len(self.samples)
                for q in range(max_rk, 0, -1):
                    if q in counter:
                        cumulative += counter[q]
                    value = q * cumulative / total_samples
                    if value > best_value:
                        best_value = value
                        best_q = q
                rubies_requested = best_q

        self.previous_requests.append(rubies_requested)
        return Info(
            sender=self.__class__.__name__,
            receiver=message.sender,
            difficulty=message.difficulty,
            message=[BaseMessageDataType(data=rubies_requested, type='custom')]
        )