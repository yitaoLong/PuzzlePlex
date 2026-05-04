from pydantic import BaseModel
from typing import List, Any

from model.base import BaseStrategy
from system.message import Info
from system.message import BaseMessageDataType
from system.message import StateLegality
from system.message import GameStatus

from puzzle.base import BasePuzzle
from prompts.exclusivity_particles import *

import random


class ExclusivityParticlesPuzzle(BasePuzzle):
    dimension: int = 0
    distance: int = 0
    particles: List[List[int]] = []
    llm_description_1: str = ''
    llm_description_2: str = ''
    count: int = 0

    def puzzle_generator(self, models: List[BaseStrategy], difficulty: str, one_shot: bool, tot: bool, iterative: bool, simplified_description: bool, legal_candidates: bool, with_history: bool, code_generation: bool, random_seed: Any, output_dir: str) -> List[Info]:
        self.difficulty = difficulty
        self.code_generation = code_generation
        self.output_dir = output_dir

        if random_seed is not None:
            self.rs = random_seed
            random.seed(random_seed)

        if self.difficulty == 'easy':
            self.dimension = random.randint(3, 7)
        elif self.difficulty == 'normal':
            self.dimension = random.randint(8, 12)

        num_particles = random.randint(2, self.dimension)
        self.distance = random.randint(1, self.dimension + 1 - num_particles)
        self.particles = []
        self.count = 0

        self.history['setting'] = {'dimension': self.dimension, 'distance': self.distance}
        self.history['state'] = []

        self.llm_description_1 = DESCRIPTION.format(dimension=self.dimension, distance=self.distance)           
        self.llm_description_2 = self.llm_description_1

        message_list = []
        model = models[0]
        if self.code_generation:
            message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=CODE_PROMPT, type='text')], generated_type='code'))
        else:
            if model.strategy_type.value != 'LLM':
                message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data={'dimension': self.dimension, 'distance': self.distance, 'particles': []}, type='custom')]))
                self.llm_description_2 += 'Here, you are the second player. You need to wait for the first player to place a particle.'
            else:
                self.llm_description_1 += 'Here, you are the first player. Please place the first particle.'
                self.llm_description_2 += 'Here, you are the second player. You need to wait for the first player to place a particle.'
                message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=self.llm_description_1, type='text')]))
                self.llm_description_1 = ''
        return message_list
            
    def state_transition_checker(self, message: Info, response: Info, model: BaseStrategy):
        result = response.message[0].data
        if result is None:
            return message, StateLegality.NONE
        else:
            if len(result) != self.dimension:
                return message, StateLegality.TERMINATE
            for value in result:
                if value not in [0, 1]:
                    return message, StateLegality.TERMINATE
            # check if the distance is satisfied
            for particle in self.particles:
                diff = 0
                for i in range(self.dimension):
                    if particle[i] != result[i]:
                        diff += 1
                if diff < self.distance:
                    return message, StateLegality.TERMINATE
            return message, StateLegality.LEGAL
        
    def state_transition(self, response: Info, model: BaseStrategy, next_model: Any):
        result = response.message[0].data
        
        self.particles.append(result)
        tmp = {'dimension': self.dimension, 'distance': self.distance, 'particles': self.particles}

        self.history['state'].append(f'turn: {self.count}, particle: {self.particles[-1]}')

        if self.count == 0:
            self.llm_description_2 += STATE_TRANSIT_PROMPT.format(particle=str(result))
        else:
            self.llm_description_1 += STATE_TRANSIT_PROMPT.format(particle=str(result))
        self.count = 1 - self.count

        if next_model.strategy_type.value == 'LLM':
            return_message = None
            if self.count == 1:
                return_message = self.llm_description_2
                self.llm_description_2 = ''
            else:
                return_message = self.llm_description_1
                self.llm_description_1 = ''
            return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=return_message, type='text')])
        else:
            return Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=tmp, type='custom')])
        
    def game_over_checker(self, model: BaseStrategy):
        return GameStatus.ONGOING

    def calculate_score(self, game_status: GameStatus, current_player: int):
        if current_player == 0:
            self.scores = ['Lose', 'Win']
        else:
            self.scores = ['Win', 'Lose']
        return 1 - current_player
        
    def get_status4simulator(self, player_idx):
        if player_idx >= len(self.scores):
            return None
        return self.scores[player_idx]

    def get_state4simulator(self) -> List[BaseMessageDataType]:
        state = ''
        if len(self.particles) == 0:
            state += 'Game starts. The dimension is {}, the distance is {}.'.format(self.dimension, self.distance) 
        else:
            state += 'The particle is placed at {}.'.format(str(self.particles[-1]))
        return [BaseMessageDataType(data=state, type='text')]

    def get_puzzle_intro4simulator(self) -> List[BaseMessageDataType]:
        puzzle_intro = PUZZLE_INTRO
        return [BaseMessageDataType(data=puzzle_intro, type='text')]

