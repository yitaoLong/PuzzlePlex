from pydantic import BaseModel
from typing import List, Any

from model.base import BaseStrategy
from system.message import Info
from system.message import BaseMessageDataType
from system.message import StateLegality
from system.message import GameStatus

from puzzle.base import BasePuzzle
from prompts.sudokill import *

import math
import random


class SudoKillPuzzle(BasePuzzle):
    result: List[List[int]] = None
    grid: List[List[int]] = None
    current_valid_moves: List[Any] = []
    prev_move: Any = None
    llm_description_1: str = ''
    llm_description_2: str = ''
    count: int = 0

    def puzzle_generator(self, models: List[BaseStrategy], difficulty: str, one_shot: bool, tot: bool, iterative: bool, simplified_description: bool, legal_candidates: bool, with_history: bool, code_generation: bool, random_seed: Any, output_dir: str) -> List[Info]:
        self.difficulty = difficulty
        self.code_generation = code_generation
        self.output_dir = output_dir
        self.one_shot = one_shot
        self.tot = tot
        self.simplified_description = simplified_description
        self.legal_candidates = legal_candidates
        self.with_history = with_history

        if random_seed is not None:
            self.rs = random_seed
            random.seed(random_seed)

        # Grid setting
        if self.difficulty == 'easy':
            settings = {'grid_size': 4, 'masked_cells_range': (8, 12)}
        elif self.difficulty == 'normal':
            settings = {'grid_size': 9, 'masked_cells_range': (30, 40)}
        grid_size = settings['grid_size']
        box_size = int(math.sqrt(grid_size))

        self.result = None
        self.grid = None
        self.current_valid_moves = []
        self.prev_move = None
        self.count = 0

        # init valid moves
        self.current_valid_moves = [(i, j) for i in range(grid_size) for j in range(grid_size)]

        # Generate a complete solution grid
        self.grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
        self.fill_grid(self.grid, grid_size, box_size)

        # Mask some cells in the grid
        masked_cells = random.randint(*settings['masked_cells_range'])
        self.mask_cells(self.grid, masked_cells)
        # data type: List[List[int]]
        self.history['setting'] = {'grid_size': grid_size, 'initial_state': str(self.grid)}
        self.history['state'] = []

        if self.one_shot:
            self.llm_description_1 = ONE_SHOT_PROMPT.format(grid=str(self.grid))
            self.llm_description_2 = self.llm_description_1
        elif self.simplified_description:
            self.llm_description_1 = SIMPLIFIED_DESCRIPTION.format(grid=str(self.grid))
            self.llm_description_2 = self.llm_description_1
        else:
            self.llm_description_1 = DESCRIPTION.format(grid=str(self.grid))
            self.llm_description_2 = self.llm_description_1

        message_list = []
        model = models[0]
        if self.code_generation:
            message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=CODE_PROMPT, type='text')], generated_type='code'))
        else:
            if model.strategy_type.value != 'LLM':
                message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=(self.prev_move, self.grid), type='custom')]))
                self.llm_description_2 += 'Here, you are the second player. You need to wait for the first player to make a move.\n'
            else:
                self.llm_description_1 += 'Here, you are the first player. You can place a number in any unoccupied space.\n'
                self.llm_description_2 += 'Here, you are the second player. You need to wait for the first player to make a move.\n'
                if self.tot:
                    message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=self.llm_description_1, type='text'), BaseMessageDataType(data=VOTE_PROMPT, type='text')]))
                elif self.legal_candidates:
                    legal_moves = self.fill_legal_moves(self.grid, len(self.grid), int(math.sqrt(len(self.grid)), None))
                    legal_candidates_message = LEGAL_CANDIDATES_PROMPT.format(legal_moves=legal_moves)
                    message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=self.llm_description_1 + legal_candidates_message, type='text')]))
                else:
                    message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=self.llm_description_1, type='text')]))
                self.llm_description_1 = ''

        return message_list

    def state_transition_checker(self, message: Info, response: Info, model: BaseStrategy):
        data = response.message[0].data
        if data is None:
            return message, StateLegality.NONE
        else:
            row_index = data[0][0]
            col_index = data[0][1]
            value = data[1]
            if not (0 <= row_index < len(self.grid) and 0 <= col_index < len(self.grid[0]) and 1 <= value <= len(self.grid)):
                return message, StateLegality.TERMINATE
            else:
                if self.valid(self.grid, value, (row_index, col_index), len(self.grid), int(math.sqrt(len(self.grid)))):
                    return message, StateLegality.LEGAL
                else:
                    return message, StateLegality.TERMINATE

    def state_transition(self, response: Info, model: BaseStrategy, next_model: Any):
        data = response.message[0].data
        row_index = data[0][0]
        col_index = data[0][1]
        value = data[1]
        self.grid[row_index][col_index] = value

        self.history['state'].append(f'turn: {self.count}, row: {row_index}, col: {col_index}, value: {value}, current_grid: {str(self.grid)}')

        # update valid moves
        self.current_valid_moves = []
        for i in range(len(self.grid)):
            if self.grid[row_index][i] == 0:
                self.current_valid_moves.append((row_index, i))
            if self.grid[i][col_index] == 0:
                self.current_valid_moves.append((i, col_index))
        if len(self.current_valid_moves) == 0:
            self.current_valid_moves = [(i, j) for i in range(len(self.grid)) for j in range(len(self.grid[0])) if self.grid[i][j] == 0]

        self.prev_move = data

        if self.count == 0:
            self.llm_description_2 += STATE_TRANSIT_PROMPT.format(row_index=row_index, col_index=col_index, value=value, grid=str(self.grid))
        else:
            self.llm_description_1 += STATE_TRANSIT_PROMPT.format(row_index=row_index, col_index=col_index, value=value, grid=str(self.grid))
        self.count = 1 - self.count

        if next_model.strategy_type.value == 'LLM':
            return_message = None
            if self.count == 1:
                return_message = self.llm_description_2
                self.llm_description_2 = ''
            else:
                return_message = self.llm_description_1
                self.llm_description_1 = ''
            if self.tot:
                return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=return_message, type='text'), BaseMessageDataType(data=VOTE_PROMPT, type='text')])
            elif not self.with_history:
                without_history_message = WITHOUT_HISTORY_PROMPT.format(row_index=row_index, col_index=col_index, value=value, grid=str(self.grid))
                return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=without_history_message, type='text')], with_history=False)
            elif self.legal_candidates:
                legal_moves = self.fill_legal_moves(self.grid, len(self.grid), int(math.sqrt(len(self.grid))), self.prev_move)
                legal_candidates_message = LEGAL_CANDIDATES_PROMPT.format(legal_moves=legal_moves)
                return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=return_message + legal_candidates_message, type='text')])
            else:
                return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=return_message, type='text')])
        else:
            return Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=(self.prev_move, self.grid), type='custom')])

    def game_over_checker(self, model: BaseStrategy):
        if len(self.current_valid_moves) == 0:
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

    def fill_grid(self, grid, grid_size, box_size):
        find = self.find_empty(grid)
        if not find:
            return True
        else:
            row, col = find

        for num in random.sample(range(1, grid_size + 1), grid_size):
            if self.valid(grid, num, (row, col), grid_size, box_size):
                grid[row][col] = num

                if self.fill_grid(grid, grid_size, box_size):
                    return True

                grid[row][col] = 0

        return False

    def find_empty(self, grid):
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == 0:
                    return i, j
        return None

    def valid(self, grid, num, pos, grid_size, box_size):
        # Check if the move is in the valid moves
        if pos not in self.current_valid_moves:
            return False

        # Check row
        if num in grid[pos[0]]:
            return False

        # Check column
        if num in [row[pos[1]] for row in grid]:
            return False

        # Check box
        box_x = pos[1] // box_size
        box_y = pos[0] // box_size

        if num in [grid[i][j] for i in range(box_y * box_size, box_y * box_size + box_size) for j in range(box_x * box_size, box_x * box_size + box_size)]:
            return False

        return True

    def mask_cells(self, grid, masked_cells):
        all_cells = [(i, j) for i in range(len(grid)) for j in range(len(grid[0]))]
        random.shuffle(all_cells)

        for i in range(masked_cells):
            row, col = all_cells[i]
            grid[row][col] = 0
        
        # update valid moves
        self.current_valid_moves = [(i, j) for i in range(len(grid)) for j in range(len(grid[0])) if grid[i][j] == 0]

    def fill_legal_moves(self, grid, grid_size, box_size, prev_move):
        if prev_move is None:
            empty_positions = [(i, j) for i in range(len(grid)) for j in range(len(grid[0])) if grid[i][j] == 0]
            legal_moves = []

            for row, col in empty_positions:
                for num in range(1, grid_size + 1):
                    if self.valid(grid, num, (row, col), grid_size, box_size):
                        legal_moves.append([(row, col), num])

            # Shuffle the legal moves
            random.shuffle(legal_moves)
            # if > 100, only keep the first 100
            if len(legal_moves) > 100:
                return legal_moves[:100]
            return legal_moves
        else:
            row_index, col_index = prev_move[0]
            value = prev_move[1]
            legal_moves = []
            
            count = 0
            for i in range(grid_size):
                if grid[row_index][i] == 0:
                    count += 1
                    for num in range(1, grid_size + 1):
                        if self.valid(grid, num, (row_index, i), grid_size, box_size):
                            legal_moves.append([(row_index, i), num])
                if grid[i][col_index] == 0:
                    count += 1
                    for num in range(1, grid_size + 1):
                        if self.valid(grid, num, (i, col_index), grid_size, box_size):
                            legal_moves.append([(i, col_index), num])

            if count == 0:
                empty_positions = [(i, j) for i in range(len(grid)) for j in range(len(grid[0])) if grid[i][j] == 0]
                for row, col in empty_positions:
                    for num in range(1, grid_size + 1):
                        if self.valid(grid, num, (row, col), grid_size, box_size):
                            legal_moves.append([(row, col), num])

            # Shuffle the legal moves
            random.shuffle(legal_moves)
            # if > 100, only keep the first 100
            if len(legal_moves) > 100:
                return legal_moves[:100]
            return legal_moves

    def get_status4simulator(self, player_idx):
        if player_idx >= len(self.scores):
            return None
        return self.scores[player_idx]

    def get_state4simulator(self) -> List[BaseMessageDataType]:
        if self.grid is None:
            return [BaseMessageDataType(data='', type='text')]
        state = ''
        for row in self.grid:
            state += str(row) + '\n'
        return [BaseMessageDataType(data=state, type='text')]

    def get_puzzle_intro4simulator(self) -> List[BaseMessageDataType]:
        puzzle_intro = PUZZLE_INTRO
        return [BaseMessageDataType(data=puzzle_intro, type='text')]