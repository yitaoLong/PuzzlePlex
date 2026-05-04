from pydantic import BaseModel
from typing import List, Any
from abc import abstractmethod

from model.base import BaseStrategy
from system.message import Info
from system.message import BaseMessageDataType
from system.message import StateLegality
from system.message import GameStatus

from puzzle.base import BasePuzzle
from prompts.larger_target import *

import random
import math
import copy


class LargerTargetPuzzle(BasePuzzle):
    bag_count: int = 0
    true_bag: List[List[int]] = []
    tracking_bag: List[List[int]] = []
    random_bag: List[List[int]] = []

    max_guess: int = 0
    guess_count: int = 0
    guess_bag: List[tuple] = []
    cnt_guess: int = 0
    value_received_1: int = 0
    value_received_2: int = 0
    value: int = 0

    llm_description_1: str = ''
    llm_description_2: str = ''
    cnt_index: int = 0

    def puzzle_generator(self, models: List[BaseStrategy], difficulty: str, one_shot: bool, tot: bool, iterative: bool, simplified_description: bool, legal_candidates: bool, with_history: bool, code_generation: bool, random_seed: Any, output_dir: str) -> List[Info]:
        self.difficulty = difficulty
        self.code_generation = code_generation
        self.output_dir = output_dir

        if random_seed is not None:
            self.rs = random_seed
            random.seed(random_seed)

        self.bag_count = 0
        self.true_bag = []
        self.tracking_bag = []
        self.random_bag = []
        self.max_guess = 0
        self.guess_count = 0
        self.guess_bag = []
        self.cnt_guess = 0
        self.value_received_1 = 0
        self.value_received_2 = 0
        self.value = 0
        self.cnt_index = 0

        if self.difficulty == 'easy':
            self.bag_count = random.randint(3, 5)
        elif self.difficulty == 'normal':
            self.bag_count = random.randint(6, 8)

        self.scores = ['0', '0']

        for i in range(self.bag_count):
            bag_len = random.randint(1, 10)
            bag = [random.randint(1, 10) for _ in range(bag_len)]
            self.true_bag.append(bag)

        self.tracking_bag = self.true_bag.copy()

        count = 0
        for bag in self.true_bag:
            count += len(bag)
        
        if count % 2 != 0:
            self.max_guess = count - 1
        else:
            self.max_guess = count

        # Generate random bags by shuffling the true bags and mapping the true to random bags by index
        indexed_true_bag = list(enumerate(self.true_bag))
        random.shuffle(indexed_true_bag)
        self.random_bag = [copy.deepcopy(list_item) for _, list_item in indexed_true_bag]
        # shuffle the list inside the random bag
        for i in range(len(self.random_bag)):
            random.shuffle(self.random_bag[i])

        init_dict = {'true_bag': self.true_bag, 'random_bag': self.random_bag, 'max_guess': self.max_guess, 'guess_bag': self.guess_bag, 'your_received_value': self.value_received_1, 'opponent_received_value': self.value_received_2, 'empty_bag': []}
        
        self.history['setting'] = {'true_bag': str(self.true_bag), 'random_bag': str(self.random_bag), 'max_guess': self.max_guess}
        self.history['state'] = []

        bag_coins = ', '.join([str(bag) for bag in self.random_bag])
        self.llm_description_1 = DESCRIPTION.format(bag_count=self.bag_count, bag_coins=bag_coins, max_guess=self.max_guess)
        self.llm_description_2 = self.llm_description_1

        message_list: List[Info] = []
        model = models[0]
        if self.code_generation:    
            message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=CODE_PROMPT, type='text')], generated_type='code'))
        else:
            if model.strategy_type.value != 'LLM':
                message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=init_dict, type='custom')]))
                self.llm_description_2 += 'You are the second player. Please wait for the first player to make a move.'
            else:
                nl_description = self.llm_description_1 + f'''You are the first player. Please make your first pick, output format should be a list `bag_index = [int]`.'''
                self.llm_description_2 += 'You are the second player. Please wait for the first player to make a move.'
                self.llm_description_1 = ''
                message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=nl_description, type='text')]))
        
        return message_list
            
    def state_transition_checker(self, message: Info, response: Info, model: BaseStrategy):
        result = response.message[0].data

        if result is None:
            return message, StateLegality.NONE
        else:
            if result not in range(self.bag_count):
                return message, StateLegality.TERMINATE
            if len(self.tracking_bag[result]) == 0:
                return message, StateLegality.TERMINATE
            else:
                return response, StateLegality.LEGAL
        
    def state_transition(self, response: Info, model: BaseStrategy, next_model: Any):
        result = response.message[0].data
        
        self.cnt_guess = result
        self.guess_count += 1
        self.value = self.tracking_bag[self.cnt_guess][0]
        self.tracking_bag[self.cnt_guess].remove(self.value)
        self.guess_bag.append((self.cnt_guess, self.value))  

        if self.guess_count % 2 == 1:
            self.value_received_1 += self.value
            self.scores[0] = str(self.value_received_1)
        else:
            self.value_received_2 += self.value
            self.scores[1] = str(self.value_received_2)

        null_bag = []
        for i in range(len(self.tracking_bag)):
            if len(self.tracking_bag[i]) == 0:
                null_bag.append(i)

        self.history['state'].append(f'turn: {(self.guess_count-1) % 2}, guess_bag: {self.guess_bag[-1][0]}, value: {self.guess_bag[-1][1]}, your_received_value: {self.value_received_1}, opponent_received_value: {self.value_received_2}, empty_bag: {null_bag}')

        nl_description = ''
        if len(self.guess_bag) >= 2:
            nl_description += f'''Your last guess was {self.guess_bag[-2][0]} and you received a coin value of {self.guess_bag[-2][1]}.'''
        
        nl_description += f'''Your opponent last guess was {self.guess_bag[-1][0]} and received a coin value of {self.guess_bag[-1][1]}.'''

        if self.guess_count % 2 == 1:
            tmp = {'true_bag': self.true_bag, 'random_bag': self.random_bag, 'max_guess': self.max_guess, 'guess_bag': self.guess_bag, 'your_received_value': self.value_received_2, 'opponent_received_value': self.value_received_1, 'empty_bag': null_bag}
            nl_description += f''' Currently, total value received by you is {self.value_received_2}, and total value received by your opponent is {self.value_received_1}.'''
        else:
            tmp = {'true_bag': self.true_bag, 'random_bag': self.random_bag, 'max_guess': self.max_guess, 'guess_bag': self.guess_bag, 'your_received_value': self.value_received_1, 'opponent_received_value': self.value_received_2, 'empty_bag': null_bag}
            nl_description += f''' Currently, total value received by you is {self.value_received_1}, and total value received by your opponent is {self.value_received_2}.'''

        if len(null_bag) > 0:
            bag_str = ','.join([str(x) for x in null_bag])
            nl_description += f'''Now Bag(s) {bag_str} is/are empty, which means you can't pick from these bags anymore.'''
        nl_description += f'''\n\nYou and your opponent have {self.max_guess - self.guess_count} picks left in total. Please make your next pick, output format should be a list `bag_index = [int]`.'''
        
        if self.cnt_index == 0:
            nl_description = self.llm_description_2 + nl_description
            self.llm_description_2 = ''
        else:
            nl_description = self.llm_description_1 + nl_description
            self.llm_description_1 = ''
        self.cnt_index = 1 - self.cnt_index


        if next_model.strategy_type.value != 'LLM':
            return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=tmp, type='custom')])
        else:
            return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=nl_description, type='text')])
        
    def game_over_checker(self, model: BaseStrategy):
        if self.guess_count == self.max_guess:
            return GameStatus.END
        else:
            return GameStatus.ONGOING

    def calculate_score(self, game_status: GameStatus, current_player: int):
        if game_status == GameStatus.END:
            if self.value_received_1 > self.value_received_2:
                self.scores = [str(self.value_received_1) + ' - Win', str(self.value_received_2) + ' - Lose']
                return 0
            elif self.value_received_1 < self.value_received_2:
                self.scores = [str(self.value_received_1) + ' - Lose', str(self.value_received_2) + ' - Win']
                return 1
            else:
                self.scores = [str(self.value_received_1) + ' - Tie', str(self.value_received_2) + ' - Tie']
                return -1
        else:
            if current_player == 0:
                self.scores = ['Invaid - Lose', 'Win']
            else:
                self.scores = ['Win', 'Invaid - Lose']
            return 1 - current_player

    def get_status4simulator(self, player_idx):
        if player_idx >= len(self.scores):
            return None
        return self.scores[player_idx]

    def get_state4simulator(self) -> List[BaseMessageDataType]:
        state = ''
        if len(self.guess_bag) == 0:
            state += 'Game starts. The random bags are ' + str(self.random_bag) + '. And the total number of picks you can make is ' + str(self.max_guess) + '.'
        else:
            state += 'Bag guess index is ' + str(self.cnt_guess) + ', value received is ' + str(self.value) + '.'
        return [BaseMessageDataType(data=state, type='text')]

    def get_puzzle_intro4simulator(self) -> List[BaseMessageDataType]:
        puzzle_intro = PUZZLE_INTRO
        return [BaseMessageDataType(data=puzzle_intro, type='text')]
        
   