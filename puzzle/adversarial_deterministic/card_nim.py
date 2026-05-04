from pydantic import BaseModel
from typing import List, Any, Dict

from model.base import BaseStrategy
from system.message import Info
from system.message import BaseMessageDataType
from system.message import StateLegality
from system.message import GameStatus

from puzzle.base import BasePuzzle
from prompts.card_nim import *

import random
import os
import json

class CardNimPuzzle(BasePuzzle):
    card_list: List[int] = []
    stone: int = 0
    
    llm_description1: str = ''
    llm_description2: str = ''
    models: List[BaseStrategy]  = []
    random_seed: Any = None
    turn: int = 0

    def puzzle_generator(self, models: List[BaseStrategy], difficulty: str, one_shot: bool, tot: bool, iterative: bool, simplified_description: bool, legal_candidates: bool, with_history: bool, code_generation: bool, random_seed: Any, output_dir: str) -> List[Info]:
        self.difficulty = difficulty
        self.code_generation = code_generation
        self.output_dir = output_dir

        if random_seed is not None:
            self.rs = random_seed
            random.seed(random_seed)

        if self.difficulty == 'easy':
            self.stone = random.randint(20, 40)
        elif self.difficulty == 'normal':
            self.stone = random.randint(40, 80)

        cards = self.generate_cards(self.stone)
        self.card_list = [cards.copy(), cards.copy()]  # Two identical sets
        self.turn = 0

        self.history['setting'] = {'stones': self.stone, 'cards': cards}
        self.history['state'] = []

        message_list = []
        model = models[0]
        if self.code_generation:
            message_list.append(Info(sender=CardNimPuzzle.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=CODE_PROMPT, type='text')], generated_type='code'))
        else:   
            self.llm_description1 = DESCRIPTION.format(cards=self.card_list[0], stones=self.stone)
            self.llm_description2 = self.llm_description1
            
            if model.strategy_type.value != 'LLM':
                self.llm_description1 += '\nYour opponent plays first.'
                message_list.append(Info(sender=CardNimPuzzle.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=(self.card_list[0], self.stone, None), type='custom')]))
            else:
                self.llm_description1 += '\nYou play first. Please play a card in the required format.'
                self.llm_description2 += '\nYour opponent plays first.'
                message_list.append(Info(sender=CardNimPuzzle.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=self.llm_description1, type='text')]))
                self.llm_description1 = ''
            
        return message_list

    def generate_cards(self, stones) -> List[int]:
        cards = None
        while True:
            tmp = random.randint(1, stones)
            if sum(range(1, tmp)) * 2 >= stones:
                cards = [i for i in range(1, tmp)]
                break
        return cards
            
    def state_transition_checker(self, message: Info, response: Info, model: BaseStrategy):
        if response.message:
            data = response.message[0].data
            if data is None:
                return message, StateLegality.NONE
            else:
                if isinstance(data, list):
                    data = data[0]
                elif isinstance(data, str):
                    if data.isdigit():
                        data = int(data)
                    else:
                        try:
                            data = eval(data)
                            if isinstance(data, list):
                                data = data[0]
                        except:
                            return message, StateLegality.TERMINATE
            try:
                cards= data
            except ValueError:
                return message, StateLegality.TERMINATE

            # Check if any card played leads to a valid game state
            if cards <= self.stone and cards in self.card_list[self.turn]:
                return message, StateLegality.LEGAL
            else:
                return message, StateLegality.TERMINATE
        else:
            return message, StateLegality.TERMINATE
    
    def state_transition(self, response: Info, model: BaseStrategy, next_model: Any):
        card_played = response.message[0].data
        
        if isinstance(card_played, int):
            pass
        elif isinstance(card_played, list):
            card_played = card_played[0]
        elif isinstance(card_played, str):
            if card_played.isdigit():
                card_played = int(card_played)
            else:
                card_played = eval(card_played)
                if isinstance(card_played, list):
                    card_played = card_played[0]
        self.stone -= card_played

        self.card_list[self.turn].remove(card_played)

        if self.turn == 0:
            self.llm_description2 += STATE_TRANSIT_PROMPT.format(card_played=card_played, stones=self.stone, your_cards=self.card_list[1-self.turn])
        else:
            self.llm_description1 = STATE_TRANSIT_PROMPT.format(card_played=card_played, stones=self.stone, your_cards=self.card_list[1-self.turn])
                   

        self.history['state'].append(f'turn: {self.turn}, card played: {card_played}, remaining stones: {self.stone}')
        self.turn = 1 - self.turn
        
        if next_model.strategy_type.value == 'LLM':
            return_message = None
            if self.turn == 1:
                return_message = self.llm_description2
                self.llm_description2 = ''
                
            else:
                return_message = self.llm_description1
                self.llm_description1 = ''

            return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=return_message, type='text')])
        
        else:
            return Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=(self.card_list[self.turn], self.stone, card_played), type='custom')])
            
    def game_over_checker(self, model: BaseStrategy):
        if self.stone <= 0:
            return GameStatus.END
        else:
            return GameStatus.ONGOING
        
    def calculate_score(self, game_status: GameStatus, current_player: int):
        if game_status == GameStatus.END:
            if current_player == 0:
                self.scores = ['Win', 'Lose']
            else:
                self.scores = ['Lose', 'Win']
            return current_player
        else:
            if current_player == 0:
                self.scores = ['Lose', 'Win']
            else:
                self.scores = ['Win', 'Lose']
            return 1 - current_player
            
    def get_status4simulator(self, player_idx: int):
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
    

 
