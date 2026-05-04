from pydantic import BaseModel
from typing import List, Any

from model.base import BaseStrategy
from system.message import Info
from system.message import BaseMessageDataType
from system.message import StateLegality
from system.message import GameStatus

from puzzle.base import BasePuzzle
from prompts.beat_or_bomb_sto import *

import random
from itertools import combinations


class BeatOrBombStoPuzzle(BasePuzzle):
    first_player_cards: List[List[str]] = []
    second_player_cards: List[List[str]] = []
    first_player_score: int = 0
    second_player_score: int = 0
    score_dict: dict = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13}
    tmp_card: List[str] = []
    first_player_remaining: List[str] = None
    second_player_remaining: List[str] = None
    card_dict: dict = None
    num_cards: int = None

    llm_description: str = ''

    def puzzle_generator(self, models: List[BaseStrategy], difficulty: str, one_shot: bool, tot: bool, iterative: bool, simplified_description: bool, legal_candidates: bool, with_history: bool, code_generation: bool, random_seed: Any, output_dir: str) -> List[Info]:
        self.difficulty = difficulty
        self.code_generation = code_generation
        self.output_dir = output_dir

        if random_seed is not None:
            self.rs = random_seed
            random.seed(random_seed)

        self.first_player_cards = []
        self.second_player_cards = []
        self.first_player_score = 0
        self.second_player_score = 0
        self.tmp_card = []
        self.first_player_remaining = None
        self.second_player_remaining = None
        self.card_dict = None
        self.num_cards = None

        if self.difficulty == 'easy':
            self.num_cards = random.randint(5, 8)
        elif self.difficulty == 'normal':
            self.num_cards = random.randint(9, 12)

        self.llm_description = DESCRIPTION.format(num_cards=self.num_cards)

        self.scores = ['0', '0']

        self.first_player_remaining, self.second_player_remaining = self.generate_initial_cards(random_seed)

        self.card_dict = {'player1 card': [], 'player2 card': [], 'player1 score': 0, 'player2 score': 0}

        self.history['setting'] = {'player1_cards': str(self.first_player_remaining), 'player2_cards': str(self.second_player_remaining)}
        self.history['state'] = []

        message_list = []
        model = models[0]
        if self.code_generation:
            message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=CODE_PROMPT, type='text')], generated_type='code'))
        else:
            if model.strategy_type.value != 'LLM':
                message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=[self.first_player_remaining.copy(), self.first_player_score, self.second_player_score, None, None], type='custom')]))
            else:
                nl_description = self.llm_description + f'''The cards you have are {self.first_player_remaining}. Please make your first move. You must output a valid list, if you do not know how to move, please randomly choose a card and randomly choose to compete or give up, and output the specific card and operation in the format `move = ['card', 'compete or give up']`. Otherwise, you will lose the game.\n\n'''
                message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=nl_description, type='text')]))
        
        return message_list

    def state_transition_checker(self, message: Info, response: Info, model: BaseStrategy):
        data = response.message[0].data
        if data is None:
            return message, StateLegality.NONE
        else:
            # legal operation
            if str(data[0]).upper() not in self.score_dict.keys() or str(data[1]).lower().strip() not in ['compete', 'give up']:
                return message, StateLegality.TERMINATE
            # card not in the remaining card list
            if len(self.tmp_card) == 0:
                if str(data[0]).upper() not in self.first_player_remaining:
                    return message, StateLegality.TERMINATE
            else:
                if str(data[0]).upper() not in self.second_player_remaining:
                    return message, StateLegality.TERMINATE
            # card not been played
            if len(self.tmp_card) == 0:
                for decision in self.first_player_cards:
                    if decision[0] == str(data[0]).upper():
                        return message, StateLegality.TERMINATE
                return response, StateLegality.LEGAL
            else:
                for decision in self.second_player_cards:
                    if decision[0] == str(data[0]).upper():
                        return message, StateLegality.TERMINATE
                return response, StateLegality.LEGAL


    def state_transition(self, response: Info, model: BaseStrategy, next_model: Any):
        data = response.message[0].data

        card = str(data[0]).upper()
        operation = str(data[1]).lower().strip()

        if len(self.tmp_card) == 0:
            self.first_player_cards.append([card, operation])
            # remove the card from the remaining card list
            self.first_player_remaining.remove(card)

            self.tmp_card.append(card)

            if next_model.strategy_type.value == 'LLM':
                nl_description = ''
                if len(self.second_player_cards) == 0:
                    nl_description = self.llm_description + f'''The cards you have are {self.second_player_remaining}. Please make your first move. You must output a valid list, if you do not know how to move, please randomly choose a card and randomly choose to compete or give up, and output the specific card and operation in the format `move = ['card', 'compete or give up']`. Otherwise, you will lose the game.\n\n'''
                else:
                    card2 = self.second_player_cards[-1][0]
                    operation2 = self.second_player_cards[-1][1]
                    card1 = self.first_player_cards[-2][0]
                    operation1 = self.first_player_cards[-2][1]
                    nl_description = f'''In the previous round, you played the card {card2} and chose to {operation2}. Your opponent played the card {card1} and chose to {operation1}. Your current score is {self.second_player_score}. Your opponent's current score is {self.first_player_score}. Your current remaining cards are {self.second_player_remaining}. Please make your next move.'''
                return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=nl_description, type='text')])
            else:
                if len(self.second_player_cards) == 0:
                    return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=[self.second_player_remaining.copy(), self.second_player_score, self.first_player_score, None, None], type='custom')])
                else:
                    card2 = self.second_player_cards[-1][0]
                    operation2 = self.second_player_cards[-1][1]
                    card1 = self.first_player_cards[-2][0]
                    operation1 = self.first_player_cards[-2][1]
                    return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=[self.second_player_remaining.copy(), self.second_player_score, self.first_player_score, (card2, operation2), (card1, operation1)], type='custom')])
        else:
            self.second_player_cards.append([card, operation])
            # remove the card from the remaining card list
            self.second_player_remaining.remove(card)

            card1 = self.first_player_cards[-1][0]
            operation1 = self.first_player_cards[-1][1]
            card2 = self.second_player_cards[-1][0]
            operation2 = self.second_player_cards[-1][1]

            self.tmp_card = []

            if operation1 == 'compete' and operation2 == 'compete':
                if self.score_dict[card1] > self.score_dict[card2]:
                    self.first_player_score += self.score_dict[card1] + self.score_dict[card2]
                    self.scores[0] = str(self.first_player_score)
                elif self.score_dict[card1] < self.score_dict[card2]:
                    self.second_player_score += self.score_dict[card1] + self.score_dict[card2]
                    self.scores[1] = str(self.second_player_score)
            elif operation1 == 'compete' and operation2 == 'give up':
                self.first_player_score += self.score_dict[card1]
                self.scores[0] = str(self.first_player_score)
            elif operation1 == 'give up' and operation2 == 'compete':
                self.second_player_score += self.score_dict[card2]
                self.scores[1] = str(self.second_player_score)

            if next_model.strategy_type.value == 'LLM':
                nl_description = f'''In the previous round, you played the card {card1} and chose to {operation1}. Your opponent played the card {card2} and chose to {operation2}. Your current score is {self.first_player_score}. Your opponent's current score is {self.second_player_score}. Your current remaining cards are {self.first_player_remaining}. Please make your next move.'''
                self.card_dict = {'player1 card': self.first_player_cards, 'player2 card': self.second_player_cards, 'player1 score': self.first_player_score, 'player2 score': self.second_player_score}
                self.history['state'].append(f'player1 card: {card1}, player1 operation: {operation1}, player2 card: {card2}, player2 operation: {operation2}, player1 score: {self.first_player_score}, player2 score: {self.second_player_score}')
                return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=nl_description, type='text')])
            else:
                self.card_dict = {'player1 card': self.first_player_cards, 'player2 card': self.second_player_cards, 'player1 score': self.first_player_score, 'player2 score': self.second_player_score}
                self.history['state'].append(f'player1 card: {card1}, player1 operation: {operation1}, player2 card: {card2}, player2 operation: {operation2}, player1 score: {self.first_player_score}, player2 score: {self.second_player_score}')
                return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=[self.first_player_remaining.copy(), self.first_player_score, self.second_player_score, (card1, operation1), (card2, operation2)], type='custom')])

    def game_over_checker(self, model: BaseStrategy):
        if len(self.first_player_remaining) == 0 and len(self.second_player_remaining) == 0:
            return GameStatus.END
        else:
            return GameStatus.ONGOING
        
    def calculate_score(self, game_status: GameStatus, current_player: int):
        if game_status == GameStatus.END:
            if self.first_player_score > self.second_player_score:
                self.scores = [str(self.first_player_score) + ' - Win', str(self.second_player_score) + ' - Lose']
                return 0
            elif self.first_player_score < self.second_player_score:
                self.scores = [str(self.first_player_score) + ' - Lose', str(self.second_player_score) + ' - Win']
                return 1
            else:
                self.scores = [str(self.first_player_score) + ' - Tie', str(self.second_player_score) + ' - Tie']
                return -1
        else:
            if current_player == 0:
                self.scores = ['Invaid - Lose', 'Win']
            else:
                self.scores = ['Win', 'Invaid - Lose']
            return 1 - current_player
        
    def generate_initial_cards(self, random_seed: Any):
        if random_seed is not None:
            self.rs = random_seed
            random.seed(random_seed)

        # Generate all combinations of keys
        all_combinations = combinations(self.score_dict.keys(), self.num_cards)

        # Calculate the sum of scores for each combination
        combination_sums = {}
        for combo in all_combinations:
            combo_sum = sum(self.score_dict[key] for key in combo)
            combination_sums.setdefault(combo_sum, []).append(combo)

        # Randomly select two combinations with the same sum
        same_sum_combos = [combo_list for combo_list in combination_sums.values() if len(combo_list) > 1]
        selected_combos = random.sample(random.choice(same_sum_combos), 2)

        # Convert combinations to lists
        list1 = list(selected_combos[0])
        list2 = list(selected_combos[1])
        return list1, list2
    
    def get_status4simulator(self, player_idx):
        if player_idx >= len(self.scores):
            return None
        return self.scores[player_idx]

    def get_state4simulator(self) -> List[BaseMessageDataType]:
        state = ''
        if len(self.first_player_cards) != 0 or len(self.second_player_cards) != 0:
            if len(self.first_player_cards) == len(self.second_player_cards):
                state += 'Played ' + self.second_player_cards[-1][0] + ' and chose to ' + self.second_player_cards[-1][1] + '. '
            else:
                state += 'Played ' + self.first_player_cards[-1][0] + ' and chose to ' + self.first_player_cards[-1][1] + '. '
        else:
            state += 'Game starts.'
        return [BaseMessageDataType(data=state, type='text')]

    def get_puzzle_intro4simulator(self) -> List[BaseMessageDataType]:
        puzzle_intro = PUZZLE_INTRO
        return [BaseMessageDataType(data=puzzle_intro, type='text')]