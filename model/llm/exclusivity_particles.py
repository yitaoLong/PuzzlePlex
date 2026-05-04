from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from abc import abstractmethod

from system.message import Info
from system.message import BaseMessageDataType
from model.strategy_type import StrategyType
from model.base import BaseStrategy
from model.util import extract_json_object

import re


class ExclusivityParticlesLLMStrategy:
    def __init__(self, model: BaseStrategy):
        self._model = model
        self.name = self._model.name
        self.history = self._model.history
        self.tmp_history: List[Any] = []
        self.tmp_completion_token_count: int = 0
        self.tmp_reasoning_content: str = ''
        self.tmp_reasoning_token_count: int = 0
        self.tmp_total_token_count: int = 0
        self.cnt_raw_output: Any = None
        self.strategy_type = StrategyType.LLM

    def update_model_field(self, field_name: str, value: Any):
        if hasattr(self._model, field_name):
            setattr(self._model, field_name, value)

    def receive_message(self, message: Info) -> Info:
        for _ in range(5):
            if message.generated_type == 'text':
                try:
                    response, self.tmp_history, self.tmp_reasoning_content, self.tmp_completion_token_count, self.tmp_reasoning_token_count, self.tmp_total_token_count = self._model.generate(message.message[0].data)
                    self.cnt_raw_output = response
                    # extract the List[int] from the response
                    extracted = re.findall(r'\[(.*?)\]', response)
                    extracted = '[' + extracted[-1] + ']'
                    extracted = eval(extracted)
                    return_message = Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=extracted, type='text')])
                    
                    # check if add into the models' arguments
                    self._model.history.extend(self.tmp_history)
                    self._model.completion_tokens.append(self.tmp_completion_token_count)
                    self._model.reasoning.append(self.tmp_reasoning_content)
                    self._model.reasoning_tokens.append(self.tmp_reasoning_token_count)
                    self._model.total_tokens.append(self.tmp_total_token_count)
                    return return_message
                except Exception as e:
                    print(e)
                    continue
            else:
                try:
                    response, self.tmp_history, self.tmp_reasoning_content, self.tmp_completion_token_count, self.tmp_reasoning_token_count, self.tmp_total_token_count = self._model.generate(message.message[0].data)
                    self.cnt_raw_output = response
                    
                    # extract the json object
                    extracted = extract_json_object(str(response))
                    if extracted:
                        return_message = Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=extracted, type='text')])
                        
                        # check if add into the models' arguments
                        self._model.history.extend(self.tmp_history)
                        self._model.completion_tokens.append(self.tmp_completion_token_count)
                        self._model.reasoning.append(self.tmp_reasoning_content)
                        self._model.reasoning_tokens.append(self.tmp_reasoning_token_count)
                        self._model.total_tokens.append(self.tmp_total_token_count)
                        return return_message
                except Exception as e:
                    print(e)
                    continue
        # If all attempts fail, return a default message
        self._model.history.extend(self.tmp_history)
        self._model.completion_tokens.append(self.tmp_completion_token_count)
        self._model.reasoning.append(self.tmp_reasoning_content)
        self._model.reasoning_tokens.append(self.tmp_reasoning_token_count)
        self._model.total_tokens.append(self.tmp_total_token_count)
        return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=None, type='text')])

    def get_raw_output4simulator(self) -> List[BaseMessageDataType]:
        return [BaseMessageDataType(data=self.cnt_raw_output, type='text')]
