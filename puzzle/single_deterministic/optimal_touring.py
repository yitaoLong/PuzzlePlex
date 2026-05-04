from pydantic import BaseModel
from typing import List, Any
from abc import abstractmethod

from model.base import BaseStrategy
from system.message import Info
from system.message import BaseMessageDataType
from system.message import StateLegality
from system.message import GameStatus

from puzzle.base import BasePuzzle
from prompts.optimal_touring import *

import random
import math
import os
import json

class OptimalTouringPuzzle(BasePuzzle):
    random_seed: Any = None
    total_value: int = 0
    num_sites: int = 0
    site_choices: List[Any] = []
    time_used: int = 0
    turn: int = 0
    value: int = 0
    
    result: Any = None
    site_data: dict = {}
    current_time: int = 0
    last_site: list = []

    def puzzle_generator(self, models: List[BaseStrategy], difficulty: str, one_shot: bool, tot: bool, iterative: bool, simplified_description: bool, legal_candidates: bool, with_history: bool, code_generation: bool, random_seed: Any, output_dir: str) -> List[Info]:
        self.difficulty = difficulty
        self.code_generation = code_generation
        self.iterative = iterative
        self.output_dir = output_dir
        
        if random_seed is not None:
            self.rs = random_seed
            random.seed(random_seed)

        self.total_value = 0
        self.num_sites = 0
        self.site_choices = []
        self.time_used = 0
        self.turn = 0
        self.value = 0
        self.result = None
        self.site_data = {}
        self.current_time = 0
        self.last_site = []
            
        if self.difficulty == 'easy':
            self.num_sites = 20
        elif self.difficulty == 'normal':
            self.num_sites = 40       
        self.site_data = self.generate_site_data(self.num_sites)

        self.history['setting'] = {'site_data': self.site_data}
        self.history['state'] = []
        
        message_list = []
        model = models[0]
        if self.code_generation:
            message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=CODE_PROMPT, type='text')], generated_type='code'))
        else:
            if model.strategy_type.value != 'LLM':
                message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=(self.site_data, self.turn, self.time_used), type='custom')]))
            else:
                if not self.iterative:
                    nl_description = DESCRIPTION.format(site_data=self.site_data)
                    message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=nl_description, type='text')]))

                else:
                    nl_description = DESCRIPTION_ITERATIVE.format(site_data=self.site_data)
                    message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=nl_description, type='text')]))
        return message_list
        
    def generate_site_data(self, num_sites):
        data = {}
        for site in range(1, num_sites + 1):
            beginhour = random.randint(0, 12)
            endhour = random.randint(beginhour + 1, 21)
            data[site] = {
                'avenue': random.randint(0, 100),
                'street': random.randint(0, 100),
                'desiredtime': random.randint(1, 200),
                'value': random.randint(1, 200),
                'beginhour': beginhour,
                'endhour': endhour
            } 
        return data
    
    def state_transition_checker(self, message: Info, response: Info, model: BaseStrategy):
        data = response.message[0].data

        if data is None:
            return message, StateLegality.NONE

        if model.strategy_type.value != 'LLM':
            for site in data:
                self.current_time += self.site_data[site]['desiredtime']
                if self.site_data[site]['endhour'] * 60 < self.current_time:
                    return message, StateLegality.TERMINATE
            if self.time_cost_checker_direct(data):
                return message, StateLegality.LEGAL
            else:
                return message, StateLegality.TERMINATE
        else:
            if not self.iterative:
                for site in data:
                    self.current_time += self.site_data[site]['desiredtime']
                    if self.site_data[site]['endhour'] * 60 < self.current_time:
                        return message, StateLegality.TERMINATE
                    if len(set(data)) != len(data):
                        return message, StateLegality.TERMINATE
                    
                if self.time_cost_checker_direct(data):
                    return message, StateLegality.LEGAL
                else:
                    return message, StateLegality.TERMINATE
            else:
                if data is None:
                    return message, StateLegality.NONE

                # Ensure data is an integer and is a valid site number
                try:
                    site_number = data[0]
                except ValueError:
                    return message, StateLegality.TERMINATE

                if site_number not in self.site_data:
                    return message, StateLegality.TERMINATE

                if site_number in self.last_site:
                    return message, StateLegality.TERMINATE

                # Record the visit to prevent repeat visits
                if self.time_cost_checker_indirect(data):
                    self.last_site.append(site_number)
                    return message, StateLegality.LEGAL
                else:
                    return message, StateLegality.TERMINATE
                
    def time_cost_checker_direct(self, travel_data):
        travel_time = self.site_data[travel_data[0]]['beginhour'] * 60
        for i in range(len(travel_data)):
            if i == 0:
                continue
            elif i != len(travel_data) - 1:
                travel_time += abs(self.site_data[travel_data[i]]['avenue'] - self.site_data[travel_data[i - 1]]['avenue']) + abs(self.site_data[travel_data[i]]['street'] - self.site_data[travel_data[i - 1]]['street'])
                travel_time += self.site_data[travel_data[i]]['desiredtime']
                if travel_time > self.site_data[travel_data[i + 1]]['endhour'] * 60:
                    return False
        return True
    
    def time_cost_checker_indirect(self, travel_data):
        if self.last_site == []:
            return True
        else:
            travel_time = self.site_data[travel_data[0]]['beginhour'] * 60
            for i in range(len(self.last_site)):
                if i == 0:
                    continue
                travel_time += abs(self.site_data[travel_data[i]]['avenue'] - self.site_data[travel_data[i - 1]]['avenue']) + abs(self.site_data[travel_data[i]]['street'] - self.site_data[travel_data[i - 1]]['street'])
                travel_time += self.site_data[travel_data[i]]['desiredtime']
                if travel_time > self.site_data[travel_data[i + 1]]['endhour'] * 60:
                    return False
            return True
                
    def state_transition(self, response: Info, model: BaseStrategy, next_model: Any):
        self.turn += 1
        self.result = response.message[0].data
        
        if model.strategy_type.value != 'LLM':
            for site in self.result:
                self.value += self.site_data[site]['value']

            self.history['state'].append(str(self.result))
            return Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data='', type='custom')])  
        elif not self.iterative:
            if isinstance(self.result, list):
                for site in self.result:
                    self.value += self.site_data[site]['value']
            
            self.history['state'].append(str(self.result))
            return Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data='', type='text')])
        else:
            try:
                site_number = self.result[0]

                site_info = self.site_data[site_number]
                self.current_time += site_info['desiredtime'] + abs(self.site_data[site_number]['avenue'] - self.site_data[self.last_site[-1]]['avenue']) + abs(self.site_data[site_number]['street'] - self.site_data[self.last_site[-1]]['street'])
                self.value += site_info['value']
                lm_description = '''You have visited site {site_number}. The current time is {self.current_time} minutes. Now the total value you have collected is {self.value}. What is the next site you want to visit? Provide the output in the following format:
Reasoning: Explain the reasoning to get the answer.
Operation: output the list in the format of `List[int] = [the site you want to visit in the time]`
output only one site number '''
                self.history['state'].append('site number: ' + str(site_number))
                return Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=lm_description, type='text')])
            except ValueError:
                return Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data="Input must be a valid integer", type='text')])
            
    def game_over_checker(self, model: BaseStrategy):
        if not self.iterative or model.strategy_type.value != 'LLM':
            return GameStatus.END
        else:
            if self.current_time > any(self.site_data[site]['endhour'] * 60 for site in self.site_data.keys()):
                return GameStatus.END
            return GameStatus.ONGOING
        
    def calculate_score(self, game_status: GameStatus, current_player: int):
        if game_status == GameStatus.END:
            return self.value
        else:
            return 0
            
    def get_status4simulator(self, player_idx: int):
        return self.value
    
    def get_state4simulator(self) -> List[BaseMessageDataType]:
        state = ''
        if len(self.history['state']) == 0:
            state += 'Site data: ' + str(self.site_data) + '\n'
        else:
            state += 'Site data: ' + str(self.site_data) + '\n'
            state += 'Last site: ' + str(self.last_site) + '\n'
            state += 'Current time: ' + str(self.current_time) + '\n'
        return [BaseMessageDataType(data=state, type='text')]
    
    def get_puzzle_intro4simulator(self) -> List[BaseMessageDataType]:
        puzzle_intro = PUZZLE_INTRO
        return [BaseMessageDataType(data=puzzle_intro, type='text')]
