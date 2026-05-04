from pydantic import BaseModel
from typing import List, Any

from model.base import BaseStrategy
from system.message import Info
from system.message import BaseMessageDataType
from system.message import StateLegality
from system.message import GameStatus
from puzzle.base import BasePuzzle
from prompts.max_maximal_cocktails import *

import random
import math


class MaxMaximalCocktailsPuzzle(BasePuzzle):
    num_nodes: int = 0
    nodes_list: List[int] = []
    edges_list: List[tuple] = []
    cnt_maximal_cocktails: int = 1
    new_maximal_cocktails: int = 0
    prev_edge: tuple = None

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
            self.num_nodes = random.randint(4, 8)
        elif self.difficulty == 'normal':
            self.num_nodes = random.randint(8, 12)

        self.nodes_list = [i for i in range(1, self.num_nodes+1)]
        self.edges_list = []
        self.cnt_maximal_cocktails = 1
        self.new_maximal_cocktails = 0
        self.prev_edge = None
        self.count = 0

        self.history['setting'] = {'nodes': self.nodes_list}
        self.history['state'] = []

        self.llm_description_1 = DESCRIPTION.format(nodes=self.nodes_list)
        self.llm_description_2 = self.llm_description_1

        message_list = []
        model = models[0]
        if self.code_generation:
            message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=CODE_PROMPT, type='text')], generated_type='code'))
        else:
            if model.strategy_type.value != 'LLM':
                message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data={'nodes': self.nodes_list, 'edges': self.edges_list, 'cnt_maximal_cocktails': self.cnt_maximal_cocktails}, type='custom')]))
                self.llm_description_2 += 'You are the second player. Please wait for the first player to make a move.\n'
            else:
                self.llm_description_1 += 'You are the first player. Please make a move.'
                self.llm_description_2 += 'You are the second player. Please wait for the first player to make a move.\n'
                message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=self.llm_description_1, type='text')]))
                self.llm_description_1 = ''
        return message_list

    def state_transition_checker(self, message: Info, response: Info, model: BaseStrategy):
        data = response.message[0].data
        if data is None:
            return message, StateLegality.NONE  
        else:
            n1, n2 = data
            if n1 not in self.nodes_list or n2 not in self.nodes_list:
                return message, StateLegality.TERMINATE
            if (n1, n2) in self.edges_list or (n2, n1) in self.edges_list:
                return message, StateLegality.TERMINATE
            return message, StateLegality.LEGAL
            
    def state_transition(self, response: Info, model: BaseStrategy, next_model: Any):
        data = response.message[0].data
        
        self.prev_edge = data
        self.edges_list.append(data)
        self.new_maximal_cocktails = self.calculate_num_maximal_cocktails()

        cnt_dict = {'nodes': self.nodes_list, 'edges': self.edges_list, 'cnt_maximal_cocktails': self.new_maximal_cocktails}

        self.history['state'].append(f'turn: {self.count}, edge: {data}, cnt_maximal_cocktails: {self.new_maximal_cocktails}')

        if self.count == 0:
            self.llm_description_2 += STATE_TRANSIT_PROMPT.format(data=data, new_maximal_cocktails=self.new_maximal_cocktails)
        else:
            self.llm_description_1 += STATE_TRANSIT_PROMPT.format(data=data, new_maximal_cocktails=self.new_maximal_cocktails)
        self.count = 1 - self.count

        if next_model.strategy_type.value != 'LLM':
            return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=cnt_dict, type='custom')])
        else:
            return_message = None
            if self.count == 1:
                return_message = self.llm_description_2
                self.llm_description_2 = ''
            else:
                return_message = self.llm_description_1
                self.llm_description_1 = ''
            return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=return_message, type='text')])
    
    def game_over_checker(self, model: BaseStrategy):
        if self.new_maximal_cocktails < self.cnt_maximal_cocktails:
            return GameStatus.END
        else:
            self.cnt_maximal_cocktails = self.new_maximal_cocktails
            self.new_maximal_cocktails = 0
            return GameStatus.ONGOING

    def calculate_score(self, game_status: GameStatus, current_player: int):
        winner = 1 - current_player
        if current_player == 0:
            self.scores = ['Loss', 'Win']
        else:
            self.scores = ['Win', 'Loss']
        return winner
    
    def calculate_num_maximal_cocktails(self):
        # find all maximal cocktails
        all_possible = []
        for i in range(1 << self.num_nodes):
            subset = []
            for j in range(self.num_nodes):
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
            for j in range(len(self.edges_list)):
                e1, e2 = self.edges_list[j]
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
    
    def get_status4simulator(self, player_idx):
        if player_idx >= len(self.scores):
            return None
        return self.scores[player_idx]

    def get_state4simulator(self) -> List[BaseMessageDataType]:
        state = ''
        if len(self.history['state']) == 0:
            state += 'Drugs: ' + str(self.nodes_list) + '\n'
        else:
            state += 'Edge added: ' + str(self.prev_edge) + '\n'
            state += 'Current edges list: ' + str(self.edges_list) + '\n'
            state += 'Current number of maximal cocktails: ' + str(self.new_maximal_cocktails) + '\n'
        return [BaseMessageDataType(data=state, type='text')]

    def get_puzzle_intro4simulator(self) -> List[BaseMessageDataType]:
        puzzle_intro = PUZZLE_INTRO
        return [BaseMessageDataType(data=puzzle_intro, type='text')]