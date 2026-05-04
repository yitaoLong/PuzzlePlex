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


class SudoKillLLMStrategy:
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
        if len(message.message) > 1 and message.generated_type == 'text':
            # tot
            response_list = []
            tot_history = []
            tot_completion_tokens = []
            tot_reasoning = []
            tot_reasoning_tokens = []
            tot_total_tokens = []
            return_value_list = []
            
            # sample 5 times
            for i in range(5):
                for _ in range(5):
                    try:
                        response, self.tmp_history, self.tmp_reasoning_content, self.tmp_completion_token_count, self.tmp_reasoning_token_count, self.tmp_total_token_count = self._model.generate(message.message[0].data, message.with_history)
                        self.cnt_raw_output = response
                        # extract the [(row_index, col_index), value] from the response
                        extracted = re.findall(r'\((\d+),(\d+)\),(\d+)', response.replace('\n', '').replace(' ', ''))
                        row_index, col_index, value = int(extracted[-1][0]), int(extracted[-1][1]), int(extracted[-1][2])
                        return_value = [(row_index, col_index), value]

                        return_value_list.append(return_value)
                        response_list.append(response)
                        tot_history.append(self.tmp_history)
                        tot_completion_tokens.append(self.tmp_completion_token_count)
                        tot_reasoning.append(self.tmp_reasoning_content)
                        tot_reasoning_tokens.append(self.tmp_reasoning_token_count)
                        tot_total_tokens.append(self.tmp_total_token_count)
                        break
                    except Exception as e:
                        print(e)
                        continue

            # vote for the best response
            vote_move = []
            for i in range(5):
                model_input = message.message[0].data + message.message[1].data + 'The following are the choices:\n'
                for j in range(len(response_list)):
                    model_input += f'Choice {j + 1}: {response_list[j]}\n'
                model_input += '''Please also provide your output in the following format:
Reasoning: Why you voted for this choice.
Operation: Specify the cell to be filled and the value to be placed in the format: `operation = [(row_index, column_index), value]`.'''
                for _ in range(5):
                    try:
                        response, self.tmp_history, self.tmp_reasoning_content, self.tmp_completion_token_count, self.tmp_reasoning_token_count, self.tmp_total_token_count = self._model.generate(model_input, message.with_history)
                        self.cnt_raw_output = response
                        # extract the [(row_index, col_index), value] from the response
                        extracted = re.findall(r'\((\d+),(\d+)\),(\d+)', response.replace('\n', '').replace(' ', ''))
                        row_index, col_index, value = int(extracted[-1][0]), int(extracted[-1][1]), int(extracted[-1][2])
                        return_value = [(row_index, col_index), value]

                        # compare with the return_value_list and get the index
                        index = -1
                        for j in range(len(return_value_list)):
                            if return_value_list[j] == return_value:
                                index = j
                                break
                        if index != -1:
                            vote_move.append(index)
                        break
                    except Exception as e:
                        print(e)
                        continue
            
            # find the most frequent index
            if len(vote_move) > 0:
                most_frequent_index = max(set(vote_move), key=vote_move.count)
                self._model.history.extend(tot_history[most_frequent_index])
                self._model.completion_tokens.append(tot_completion_tokens[most_frequent_index])
                self._model.reasoning.append(tot_reasoning[most_frequent_index])
                self._model.reasoning_tokens.append(tot_reasoning_tokens[most_frequent_index])
                self._model.total_tokens.append(tot_total_tokens[most_frequent_index])
                return_value = return_value_list[most_frequent_index]
                return_message = Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=return_value, type='text')])
                return return_message
        else:
            for _ in range(5):
                if message.generated_type == 'text':
                    try:
                        response, self.tmp_history, self.tmp_reasoning_content, self.tmp_completion_token_count, self.tmp_reasoning_token_count, self.tmp_total_token_count = self._model.generate(message.message[0].data, message.with_history)
                        self.cnt_raw_output = response
                        # extract the [(row_index, col_index), value] from the response
                        extracted = re.findall(r'\((\d+),(\d+)\),(\d+)', response.replace('\n', '').replace(' ', ''))
                        row_index, col_index, value = int(extracted[-1][0]), int(extracted[-1][1]), int(extracted[-1][2])
                        return_value = [(row_index, col_index), value]
                        return_message = Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=return_value, type='text')])
                        
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