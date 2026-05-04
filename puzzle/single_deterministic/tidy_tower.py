from pydantic import BaseModel
from typing import List, Any

from model.base import BaseStrategy
from system.message import Info
from system.message import BaseMessageDataType
from system.message import StateLegality
from system.message import GameStatus

from puzzle.base import BasePuzzle
from prompts.tidy_tower import *

import random
import math
import os
import json


class TidyTowerPuzzle(BasePuzzle):
    grid: list = []
    result: Any = None
    nl_description: str = ''
    rotation: list = ['R', 'Y', 'B', 'G']
    random_seed: Any = None
    height: int = 0
    sequence: list = [['R', 'G', 'B', 'Y'], ['G', 'B', 'Y', 'R'], ['B', 'Y', 'R', 'G'], ['Y', 'R', 'G', 'B']]
    method: List[int] = []
    maxtime: int = 20
    turn: int = 0

    def puzzle_generator(self, models: List[BaseStrategy], difficulty: str, one_shot: bool, tot: bool, iterative: bool, simplified_description: bool, legal_candidates: bool, with_history: bool, code_generation: bool, random_seed: Any, output_dir: str) -> List[Info]:
        self.difficulty = difficulty
        self.code_generation = code_generation
        self.output_dir = output_dir
        self.one_shot = one_shot
        self.tot = tot
        self.simplified_description = simplified_description
        self.legal_candidates = legal_candidates
        self.with_history = with_history
        self.iterative = iterative

        # Define the grid sizes and other parameters for each difficulty level
        difficulty_settings = {
            'easy': {'tower_height': 6, 'num_colors': 4},
            'normal': {'tower_height': 10, 'num_colors': 4},
        }

        self.turn = 0
        
        settings = difficulty_settings.get(self.difficulty, difficulty_settings[self.difficulty])
        tower_height = settings['tower_height']
        num_colors = settings['num_colors']
        
        if random_seed is not None:
            self.rs = random_seed
            random.seed(random_seed)

        # Generate a tower with random orientations
        self.grid = self.generate_tower(tower_height, random_seed)

        self.history['setting'] = {'initial_tower': str(self.grid)}
        self.history['state'] = []

        message_list = []
        model = models[0]
        if self.code_generation:
            message_list.append(Info(sender=TidyTowerPuzzle.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=CODE_PROMPT, type='text')], generated_type='code'))
        else:
            # Generate message
            if model.strategy_type.value != 'LLM':  
                message_list.append(Info(sender=TidyTowerPuzzle.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=self.grid, type='custom')]))
            else:
                if not self.iterative:
                    if self.simplified_description:
                        nl_description = SIMPLIFIED_DESCRIPTION.format(num_cubes=tower_height, tower=self.grid, max_height=tower_height - 1)
                    elif self.one_shot:
                        nl_description = ONE_SHOT_PROMPT.format(num_cubes=tower_height, tower=self.grid, max_height=tower_height - 1)
                    else:
                        nl_description = DESCRIPTION.format(num_cubes=tower_height, tower=self.grid, max_height=tower_height - 1)
                    message_list.append(Info(sender=TidyTowerPuzzle.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=nl_description, type='text')]))
                else:
                    nl_description = DESCRIPTION_ITERATIVE.format(num_cubes=tower_height, tower=self.grid, max_height=tower_height - 1)
                    if self.tot:
                        message_list.append(Info(sender=TidyTowerPuzzle.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=nl_description, type='text'), BaseMessageDataType(data=VOTE_PROMPT, type='text')]))
                    elif self.legal_candidates:
                        legal_moves = self.generate_random_legal_moves(self.grid)
                        legal_candidates_message = LEGAL_CANDIDATES_PROMPT.format(legal_moves=legal_moves)
                        message_list.append(Info(sender=TidyTowerPuzzle.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=nl_description + legal_candidates_message, type='text')]))
                    else:
                        message_list.append(Info(sender=TidyTowerPuzzle.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=nl_description, type='text')]))
        return message_list

    def generate_random_legal_moves(self, tower: List[str]):
        legal_moves = []
        for _ in range(10):
            cube_index = random.randint(0, len(tower) - 1)
            rotation = random.randint(1, 4)
            holding = random.randint(0, 1)
            legal_moves.append([cube_index, rotation, holding])
        return legal_moves

    def generate_tower(self, tower_height: int, random_seed: Any):
        colors = ['R', 'Y', 'B', 'G'] 
        tower = []

        if random_seed is not None:
            random.seed(random_seed)

        for i in range(tower_height):
            if i == tower_height - 1:
                # Select a different color for the last cube
                cube_colors = [color for color in colors if color != tower[i-1]][0]
            else:
                start_index = random.randint(0, 3)  
                cube_colors = colors[start_index] 
            tower.append(cube_colors)

        return tower
        
    def state_transition_checker(self, message: Info, response: Info, model: BaseStrategy):
        if model.strategy_type.value != 'LLM':
            return message, StateLegality.LEGAL
        else:
            if not self.iterative:
                data = response.message[0].data
                if data is None:
                    return message, StateLegality.NONE
                else:
                    if not isinstance(data, list):
                        return message, StateLegality.TERMINATE
                    for action in data:
                        if not (isinstance(action, list) and len(action) == 3):
                            return message, StateLegality.TERMINATE
                        if not all(isinstance(x, int) for x in action):
                            return message, StateLegality.TERMINATE
                    return message, StateLegality.LEGAL
            else:
                data = response.message[0].data
                if data is None:
                    return message, StateLegality.NONE
                else:
                    cube_index, rota, holding = data
                    if not isinstance(data, list):
                        data = eval(data)
    
                    if not isinstance(cube_index, int):
                        cube_index = int(cube_index)
                    if not isinstance(rota, int):
                        rota = int(rota)
                    if not isinstance(holding, int):
                        holding = int(holding)
                    if cube_index < 0 or cube_index >= len(self.grid):
                        return message, StateLegality.TERMINATE
                    if rota < 0 or rota > 4:
                        return message, StateLegality.TERMINATE
                    if holding != 0 and holding != 1:
                        return message, StateLegality.TERMINATE

                    return message, StateLegality.LEGAL
                
    def state_transition(self, response: Info, model: BaseStrategy, next_model: Any):
        if model.strategy_type.value != 'LLM':
            self.method = response.message[0].data
            for action in self.method:
                self.rotate(action)
                self.history['state'].append(f'Action: {str(action)}, Tower: {str(self.grid)}')
            return Info(sender=TidyTowerPuzzle.__name__, receiver=model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data='', type='custom')])
        else:
            if not self.iterative:
                self.result = response.message[0].data
                for action in self.result:
                    self.rotate(action)
                    self.history['state'].append(f'Action: {str(action)}, Tower: {str(self.grid)}')
                return Info(sender=TidyTowerPuzzle.__name__, receiver=model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data='', type='custom')])
            else:
                self.turn += 1
                data = response.message[0].data
                cube_index, rota, holding = data
                if not isinstance(data, list):
                    data = eval(data)
 
                if not isinstance(cube_index, int):
                    cube_index = int(cube_index)
                if not isinstance(rota, int):
                    rota = int(rota)
                if not isinstance(holding, int):
                    holding = int(holding)
                self.method = [cube_index, rota, holding]
                self.rotate(self.method)
                self.history['state'].append(f'Action: {str(self.method)}, Tower: {str(self.grid)}')

                return_message = '''Now the tower has been rotated. Please continue solving: {}. Output the next operation in the format: 'operation = [Cube index, Rotation, Holding]'.'''.format(self.grid)
                if self.tot:
                    return Info(sender=TidyTowerPuzzle.__name__, receiver=model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=return_message, type='text'), BaseMessageDataType(data=VOTE_PROMPT, type='text')])
                elif not self.with_history:
                    without_history_message = WITHOUT_HISTORY_PROMPT.format(num_cubes=len(self.grid), tower=self.grid, max_height=len(self.grid) - 1, previous_operation=self.method)
                    return Info(sender=TidyTowerPuzzle.__name__, receiver=model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=without_history_message, type='text')], with_history=False)
                elif self.legal_candidates:
                    legal_moves = self.generate_random_legal_moves(self.grid)
                    legal_candidates_message = LEGAL_CANDIDATES_PROMPT.format(legal_moves=legal_moves)
                    return Info(sender=TidyTowerPuzzle.__name__, receiver=model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=return_message + legal_candidates_message, type='text')])
                else:
                    return Info(sender=TidyTowerPuzzle.__name__, receiver=model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=return_message, type='text')])

    def rotate(self, action):
        cube_index, rotation, holding = map(int, action)
        
        color_sequence = ['R', 'Y', 'B', 'G']
        
        if holding == 0:
            self.grid[cube_index] = color_sequence[(color_sequence.index(self.grid[cube_index]) + rotation) % 4]
            
        else:
            self.grid[cube_index] = color_sequence[(color_sequence.index(self.grid[cube_index]) + rotation) % 4]
            for i in range(cube_index + 1, len(self.grid)):
                self.grid[i] = color_sequence[(color_sequence.index(self.grid[i]) + rotation) % 4]

    def game_over_checker(self, model: BaseStrategy):
        if model.strategy_type.value == 'Custom':
            return GameStatus.END
        else:
            if not self.iterative:
                return GameStatus.END
            else:
                if self.turn >= self.maxtime:
                    return GameStatus.END
                elif len(set(self.grid)) == 1:
                    return GameStatus.END
                else:
                    return GameStatus.ONGOING
            
    def calculate_score(self, game_status: GameStatus, current_player: int):
        if game_status == GameStatus.END:
            if len(set(self.grid)) == 1:
                self.scores = ['Success']
                return 1
            self.scores = ['Fail']
            return 0
        else:
            self.scores = ['Fail']
            return 0
        
    def get_status4simulator(self, player_idx: int):
        if len(self.scores) == 0:
            return None
        else:
            return self.scores[0]
    
    def get_state4simulator(self):
        if self.grid is None:
            return [BaseMessageDataType(data='', type='text')]
        else:
            state = str(self.grid)
            if self.iterative:
                state = f"Current tower: {state}, Previous operation: {self.method}"
            else:
                state = f"Current tower: {state}"
        return [BaseMessageDataType(data=state, type='text')]
    
    def get_puzzle_intro4simulator(self) -> List[BaseMessageDataType]:
        puzzle_intro = PUZZLE_INTRO
        return [BaseMessageDataType(data=puzzle_intro, type='text')]


        

