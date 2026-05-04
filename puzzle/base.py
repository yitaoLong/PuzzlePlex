from pydantic import BaseModel
from typing import List, Any, Dict
from abc import abstractmethod

from model.base import BaseStrategy
from system.message import Info
from system.message import BaseMessageDataType
from system.message import StateLegality
from system.message import GameStatus

import json
import os


class BasePuzzle(BaseModel):
    difficulty: str = ''
    one_shot: bool = False
    tot: bool = False
    iterative: bool = False
    simplified_description: bool = False
    legal_candidates: bool = False
    with_history: bool = True
    code_generation: bool = False
    rs: Any = None
    scores: List[Any] = []
    history: Dict[str, Any] = {}
    output_dir: str= ''

    @abstractmethod
    def puzzle_generator(self, models: List[BaseStrategy], difficulty: str, one_shot: bool, tot: bool, iterative: bool, simplified_description: bool, legal_candidates: bool, with_history: bool, code_generation: bool, random_seed: Any, output_dir: str):
        pass

    @abstractmethod
    def state_transition_checker(self, message: Info, response: Info, model: BaseStrategy):
        pass

    @abstractmethod
    def state_transition(self, response: Info, model: BaseStrategy, next_model: Any):
        pass

    @abstractmethod
    def game_over_checker(self, model: BaseStrategy):
        pass

    def extract_llm_history(self, models: List[BaseStrategy], with_history: bool):
        llm_history = []

        for model in models:
            if model.strategy_type.value == 'LLM':
                llm_history.append(model._model.get_formated_history(with_history))
            else:
                llm_history.append([])

        return llm_history

    def save_file(self, score, models: List[BaseStrategy], state_legality: StateLegality, with_history: bool):
        if not os.path.exists(self.output_dir + '/' + str(self.__class__.__name__) + '.json'):
            with open(self.output_dir + '/' + str(self.__class__.__name__) + '.json', 'w') as f:
                json.dump([], f, indent=4)
        with open(self.output_dir + '/' + str(self.__class__.__name__) + '.json', 'r') as f:
            data = json.load(f)

        llm_history = self.extract_llm_history(models, with_history)
        accumulated_token_count = []
        for model in models:
            if model.strategy_type.value == 'LLM':
                accumulated_token_count.append(model._model.total_tokens)
            else:
                accumulated_token_count.append([])

        model_name = []
        instruction_based = False 
        for model in models:
            if model.strategy_type.value == 'LLM':
                instruction_based = True
                model_name.append(model.__class__.__name__ + ':' + model.name)
            else:
                if model.name != 'custom':
                    model_name.append(model.__class__.__name__ + ':' + model.name)
                else:
                    model_name.append(model.__class__.__name__)
        model_strategy_type = [model.strategy_type.value for model in models]

        total_usage = 0
        for model in models:
            if model.strategy_type.value == 'LLM':
                total_usage += model._model.total_usage
            else:
                total_usage += 0

        if instruction_based:
            data.append({'history': self.history, 'score': score, 'difficulty': self.difficulty, 'iterative': self.iterative, 'simplified_description': self.simplified_description, 'legal_candidates': self.legal_candidates, 'code_generation': self.code_generation, 'llm_history': llm_history, 'accumulated_token_count': accumulated_token_count, 'total_usage': total_usage, 'model_name': model_name, 'model_strategy_type': model_strategy_type, 'random_seed': self.rs, 'state_legality': str(state_legality)})
        else:
            data.append({'score': score, 'difficulty': self.difficulty, 'model_name': model_name, 'model_strategy_type': model_strategy_type, 'random_seed': self.rs, 'state_legality': str(state_legality)})
        with open(self.output_dir + '/' + str(self.__class__.__name__) + '.json', 'w') as f:
            json.dump(data, f, indent=4)

    def extract_code(self, message: Info):
        reasoning = ''
        code = ''

        if message.message:
            data = message.message[0].data
            if data is not None:
                if isinstance(data, dict):
                    if 'reasoning' in data:
                        reasoning = data['reasoning']
                    if 'code' in data:
                        code = data['code']

        return reasoning, code

    def save_code(self, response: Info, models: List[BaseStrategy]):
        if not os.path.exists(self.output_dir + '/' + str(self.__class__.__name__) + '.json'):
            with open(self.output_dir + '/' + str(self.__class__.__name__) + '.json', 'w') as f:
                json.dump([], f, indent=4)
        with open(self.output_dir + '/' + str(self.__class__.__name__) + '.json', 'r') as f:
            data = json.load(f)

        reasoning, code = self.extract_code(response)

        model_name = [] 
        for model in models:
            if model.strategy_type.value == 'LLM':
                model_name.append(model.__class__.__name__ + ':' + model.name)
            else:
                model_name.append(model.__class__.__name__)

        llm_history = self.extract_llm_history(models, True)
        accumulated_token_count = []
        for model in models:
            if model.strategy_type.value == 'LLM':
                accumulated_token_count.append(model._model.total_tokens)
            else:
                accumulated_token_count.append([])

        total_usage = 0
        for model in models:
            if model.strategy_type.value == 'LLM':
                total_usage += model._model.total_usage
            else:
                total_usage += 0

        index = len(data)
        data.append({'reasoning': reasoning, 'code': code, 'model_name': model_name, 'index': index, 'accumulated_token_count': accumulated_token_count, 'total_usage': total_usage, 'llm_history': llm_history})

        with open(self.output_dir + '/' + str(self.__class__.__name__) + '.json', 'w') as f:
            json.dump(data, f, indent=4)

    @abstractmethod
    def calculate_score(self, game_status: GameStatus, current_player: int):
        pass

    @abstractmethod
    def get_status4simulator(self, player_idx: int):
        pass

    @abstractmethod
    def get_state4simulator(self):
        pass

    @abstractmethod
    def get_puzzle_intro4simulator(self):
        pass