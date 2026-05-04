from pydantic import BaseModel
from typing import List, Any
from abc import abstractmethod

from model.base import BaseStrategy
from system.message import Info
from system.message import BaseMessageDataType
from system.message import StateLegality
from system.message import GameStatus

from puzzle.base import BasePuzzle
from prompts.ruby_risks import *

import random
import math
import os
import json
 
class RubyRisksPuzzle(BasePuzzle):
    ruby_list: List[int] = []
    feedback: List[int] = []
    llm_description: str = ''
    request: List[int] = None
    turn: int = 0
    total_rubies: int = 0
    boxes: int = None
    random_seed: Any = None
    difference: int = 0

    def puzzle_generator(self, models: List[BaseStrategy], difficulty: str, one_shot: bool, tot: bool, iterative: bool, simplified_description: bool, legal_candidates: bool, with_history: bool, code_generation: bool, random_seed: Any, output_dir: str) -> List[Info]:
        self.difficulty = difficulty
        self.code_generation = code_generation
        self.output_dir = output_dir

        if random_seed is not None:
            self.rs = random_seed
            random.seed(random_seed)

        self.ruby_list = []
        self.feedback = []
        self.request = []
        self.turn = 0
        self.total_rubies = 0
        self.boxes = None
        self.difference = 0

        if self.difficulty == 'easy':
            self.boxes = random.randint(3, 7)
            self.total_rubies = random.randint(30, 70)
            self.difference = 4
        elif self.difficulty == 'normal':
            self.boxes = random.randint(8, 12)
            self.total_rubies = random.randint(80, 120)
            self.difference = 4

        self.request = [None] * self.boxes
        if self.total_rubies == 0:
            self.ruby_list = [0] * self.boxes
        else:
            self.ruby_list = self.generate_ruby_distribution(self.total_rubies, self.difference)

        self.history['setting'] = {'boxes': str(self.ruby_list), 'total_rubies': str(self.total_rubies)}
        self.history['state'] = []

        message_list = []
        model = models[0]
        if self.code_generation:
            message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=CODE_PROMPT, type='text')], generated_type='code'))
        else:
            if model.strategy_type.value != 'LLM':
                self.turn += 1
                message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=(self.total_rubies, self.turn, self.feedback, self.boxes), type='custom')]))
                return message_list
            else:
                self.turn += 1
                self.llm_description = DESCRIPTION.format(boxes=self.boxes, total_rubies=self.total_rubies, turn=self.turn)
                message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=(self.llm_description), type='custom')]))
        
        return message_list

    def generate_ruby_distribution(self, total_rubies, difference):
        while True:

            ruby_base = [random.randint(1, self.total_rubies - self.boxes) for _ in range(self.boxes-1)]

            ruby_base.append(self.total_rubies - sum(ruby_base))


            if all(ruby > 0 for ruby in ruby_base):

                max_index = ruby_base.index(max(ruby_base))
                min_index = ruby_base.index(min(ruby_base))


                if ruby_base[max_index] >= ruby_base[min_index] + difference:

                    if (ruby_base[max_index] + ruby_base[min_index]) % 2 == 0:
                        average = (ruby_base[max_index] + ruby_base[min_index]) // 2
                        ruby_base[max_index] = average + difference // 2
                        ruby_base[min_index] = average - difference // 2
                    else:

                        average = (ruby_base[max_index] + ruby_base[min_index]) // 2
                        ruby_base[max_index] = average + (difference // 2 + 1)
                        ruby_base[min_index] = average - (difference // 2)
                    

                    if all(ruby > 0 for ruby in ruby_base):
                        break

        return ruby_base

    def state_transition_checker(self, message: Info, response: Info, model: BaseStrategy):
        requested_rubies = response.message[0].data
        
        if isinstance(requested_rubies, list):
            requested_rubies = requested_rubies[0]
        if requested_rubies is None:
            return message, StateLegality.NONE
        if type(requested_rubies) != int:
            return message, StateLegality.TERMINATE
        return message, StateLegality.LEGAL


    def state_transition(self, response: Info, model: BaseStrategy, next_model: Any):
        request_rubies = response.message[0].data
        if isinstance(request_rubies, list):
            request_rubies = request_rubies[0]
        self.request[self.turn-1] = request_rubies
        if request_rubies > self.ruby_list[self.turn-1]:
            self.feedback.append(0)
        else:
            self.feedback.append(request_rubies)
        self.turn += 1
        self.scores = [str(sum(self.feedback))]  
        self.history['state'].append(f'turn: {self.turn-1}, request: {self.request[self.turn-2]}, feedback: {self.feedback[self.turn-2]}')
        if model.strategy_type.value != 'LLM':
            return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=(self.total_rubies, self.turn, self.feedback, self.boxes), type='custom')])
        else:
            nl_description = STATE_TRANSIT_PROMPT.format(turn=self.turn, rubies=self.feedback[self.turn-2])
            return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=nl_description, type='text')])
 
    def game_over_checker(self, model: BaseStrategy):
        if self.turn > self.boxes:
            return GameStatus.END  
        return GameStatus.ONGOING

    def calculate_score(self, game_status: GameStatus, current_player: int):
        if game_status == GameStatus.END:
            self.scores = [str(sum(self.feedback))]
            return sum(self.feedback)
        else:
            self.scores = ['0']
            return 0
        
    def get_status4simulator(self, player_idx):
        if player_idx >= len(self.scores):
            return None
        return self.scores[player_idx]

    def get_state4simulator(self) -> List[BaseMessageDataType]:
        if len(self.history['state']) == 0:
            return [BaseMessageDataType(data=str(self.history['setting']), type='text')]
        return [BaseMessageDataType(data=str(self.history['state'][-1]), type='text')]

    def get_puzzle_intro4simulator(self) -> List[BaseMessageDataType]:
        puzzle_intro = PUZZLE_INTRO
        return [BaseMessageDataType(data=puzzle_intro, type='text')]
    
    
