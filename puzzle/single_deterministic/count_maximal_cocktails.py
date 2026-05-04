from pydantic import BaseModel
from typing import List, Any

from model.base import BaseStrategy
from system.message import Info
from system.message import BaseMessageDataType
from system.message import StateLegality
from system.message import GameStatus

from puzzle.base import BasePuzzle
from prompts.count_maximal_cocktails import *

import random
import math


class CountMaximalCocktailsPuzzle(BasePuzzle):
    num_nodes: int = 0
    num_edges: int = 0
    nodes_list: List[int] = []
    edges_list: List[tuple] = []
    result: Any = None

    def puzzle_generator(self, models: List[BaseStrategy], difficulty: str, one_shot: bool, tot: bool, iterative: bool, simplified_description: bool, legal_candidates: bool, with_history: bool, code_generation: bool, random_seed: Any, output_dir: str) -> List[Info]:
        self.difficulty = difficulty
        self.code_generation = code_generation
        self.output_dir = output_dir

        if random_seed is not None:
            self.rs = random_seed
            random.seed(random_seed)

        self.num_nodes = random.randint(3, 10)
        self.nodes_list = [i for i in range(1, self.num_nodes+1)]

        all_possible_edges = []
        for i in range(1, self.num_nodes+1):
            for j in range(i+1, self.num_nodes+1):
                all_possible_edges.append((i, j))

        self.num_edges = random.randint(0, int(len(all_possible_edges)/2))
        self.edges_list = random.sample(all_possible_edges, self.num_edges)

        init_dict = {'nodes': self.nodes_list, 'edges': self.edges_list}

        self.history['setting'] = {'nodes': str(self.nodes_list), 'edges': str(self.edges_list)}
        self.history['state'] = []

        message_list = []
        model = models[0]
        if self.code_generation:
            message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=CODE_PROMPT, type='text')], generated_type='code'))
        else:
            if model.strategy_type.value != 'LLM':
                message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=init_dict, type='custom')]))
            else:
                if self.difficulty == 'easy':
                    # find the number of maximal cocktails
                    nl_description = DESCRIPTION_EASY.format(nodes_list=self.nodes_list, edges_list=self.edges_list)
                    message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=nl_description, type='text')]))
                elif self.difficulty == 'normal':
                    # find all the set of maximal cocktails
                    nl_description = DESCRIPTION_NORMAL.format(nodes_list=self.nodes_list, edges_list=self.edges_list)
                    message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=nl_description, type='text')]))
        return message_list

    def state_transition_checker(self, message: Info, response: Info, model: BaseStrategy):
        if response.message[0].data is None:
            return message, StateLegality.NONE
        else:
            return message, StateLegality.LEGAL
            
    def state_transition(self, response: Info, model: BaseStrategy, next_model: Any):
        data = response.message[0].data
        self.result = data

        self.history['state'].append('Model output: ' + str(data))
        return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=data, type='text')])
    
    def game_over_checker(self, model: BaseStrategy):
        return GameStatus.END

    def calculate_score(self, game_status: GameStatus, current_player: int):
        if game_status == GameStatus.END:
            gt = self.calculate_gt()
            self.history['state'].append('Ground truth: ' + str(gt))
            if self.difficulty == 'easy':
                if self.result == gt:
                    self.scores.append('Success')
                    return 1
                else:
                    self.scores.append('Fail')
                    return 0
            elif self.difficulty == 'normal':
                is_same = True
                for cocktail in self.result:
                    if set(cocktail) not in gt:
                        is_same = False
                        break
                if is_same:
                    if len(self.result) == len(gt):
                        self.scores.append('Success')
                        return 1
                    else:
                        self.scores.append('Fail')
                        return 0
                else:
                    self.scores.append('Fail')
                    return 0
        else:
            self.scores.append('Fail')
            return 0
    
    def calculate_gt(self):
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
        
        if self.difficulty == 'easy':
            return len(maximal_cocktails)
        elif self.difficulty == 'normal':
            return maximal_cocktails
    
    def get_status4simulator(self, player_idx):
        return self.scores[-1]
    
    def get_state4simulator(self) -> List[BaseMessageDataType]:
        state = ''
        if len(self.history['state']) == 0:
            state += 'Drug list: ' + str(self.nodes_list) + '\n'
            state += 'Bad interaction list: ' + str(self.edges_list) + '\n'
        elif len(self.history['state']) == 1:
            if self.difficulty == 'easy':
                state += 'Model output: The number of maximal cocktails is ' + str(self.result) + '\n'
            elif self.difficulty == 'normal':
                state += 'Model output: The maximal cocktails are ' + str(self.result) + '\n'
        return [BaseMessageDataType(data=state, type='text')]
    
    def get_puzzle_intro4simulator(self) -> List[BaseMessageDataType]:
        puzzle_intro = PUZZLE_INTRO
        return [BaseMessageDataType(data=puzzle_intro, type='text')]
    
