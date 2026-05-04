from pydantic import BaseModel
from typing import List, Any

from model.base import BaseStrategy
from system.message import Info
from system.message import BaseMessageDataType
from system.message import StateLegality
from system.message import GameStatus

from puzzle.base import BasePuzzle
from prompts.sudokill_m import *

from PIL import Image, ImageDraw, ImageFont
import random
import math

import os
import json


class SudoKillMPuzzle(BasePuzzle):
    result: List[List[int]] = None
    grid: List[List[int]] = None
    grid_image: Any = None
    current_valid_moves: List[Any] = []
    prev_move: Any = None
    llm_description_1: str = ''
    llm_description_2: str = ''
    message_data_1: List[Any] = []
    message_data_2: List[Any] = []
    count: int = 0

    def puzzle_generator(self, models: List[BaseStrategy], difficulty: str, one_shot: bool, tot: bool, iterative: bool, simplified_description: bool, legal_candidates: bool, with_history: bool, code_generation: bool, random_seed: Any, output_dir: str) -> List[Info]:
        self.difficulty = difficulty
        self.output_dir = output_dir

        if random_seed is not None:
            self.rs = random_seed
            random.seed(random_seed)

        self.llm_description_1 = DESCRIPTION 
        self.llm_description_2 = self.llm_description_1

        self.result = None
        self.grid = None
        self.grid_image = None
        self.current_valid_moves = []
        self.prev_move = None
        self.message_data_1 = []
        self.message_data_2 = []
        self.count = 0

        # Grid setting
        if self.difficulty == 'easy':
            settings = {'grid_size': 4, 'masked_cells_range': (8, 12)}
        elif self.difficulty == 'normal':
            settings = {'grid_size': 9, 'masked_cells_range': (30, 40)}
        grid_size = settings['grid_size']
        box_size = int(math.sqrt(grid_size))

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

        self.grid_image = self.draw_sudoku_board(self.grid, grid_size)

        self.llm_description_1 += 'The following image shows the initial grid.\n'
        self.llm_description_2 += 'The following image shows the initial grid.\n'
        self.message_data_1.append(BaseMessageDataType(data=self.llm_description_1, type='text'))
        self.message_data_2.append(BaseMessageDataType(data=self.llm_description_2, type='text'))
        self.message_data_1.append(BaseMessageDataType(data=self.grid_image, type='image'))
        self.message_data_2.append(BaseMessageDataType(data=self.grid_image, type='image'))

        message_list: List[Info] = []
        model = models[0]
        if model.strategy_type.value != 'LLM':
            message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=(self.prev_move, self.grid), type='custom')]))
            self.llm_description_2 = 'Here, you are the second player. You need to wait for the first player to make a move.\n'
            self.message_data_2.append(BaseMessageDataType(data=self.llm_description_2, type='text'))
            return message_list
        else:
            self.llm_description_1 = 'Here, you are the first player. You can place a number in any unoccupied space.\n'
            self.llm_description_2 = 'Here, you are the second player. You need to wait for the first player to make a move.\n'
            self.message_data_1.append(BaseMessageDataType(data=self.llm_description_1, type='text'))
            self.message_data_2.append(BaseMessageDataType(data=self.llm_description_2, type='text'))
            message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=self.message_data_1))
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
        self.grid_image = self.draw_sudoku_board(self.grid, len(self.grid))

        self.history['state'].append(f'turn: {self.count}, move: {data}, grid: {self.grid}')

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
            self.message_data_1 = []
            self.llm_description_2 = '''Your competitive move is to fill the cell at ({}, {}) with the value {}. The current grid is '''.format(row_index, col_index, value)
            self.message_data_2.append(BaseMessageDataType(data=self.llm_description_2, type='text'))
            self.message_data_2.append(BaseMessageDataType(data=self.grid_image, type='image'))
            self.llm_description_2 = 'Now it is your turn.'
            self.message_data_2.append(BaseMessageDataType(data=self.llm_description_2, type='text'))
        else:
            self.message_data_2 = []
            self.llm_description_1 = '''Your competitive move is to fill the cell at ({}, {}) with the value {}. The current grid is '''.format(row_index, col_index, value)
            self.message_data_1.append(BaseMessageDataType(data=self.llm_description_1, type='text'))
            self.message_data_1.append(BaseMessageDataType(data=self.grid_image, type='image'))
            self.llm_description_1 = 'Now it is your turn.'
            self.message_data_1.append(BaseMessageDataType(data=self.llm_description_1, type='text'))
        self.count = 1 - self.count

        if next_model.strategy_type.value == 'LLM':
            return_message = None
            if self.count == 1:
                return_message = self.message_data_2
            else:
                return_message = self.message_data_1
            return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=return_message)
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

    def draw_sudoku_board(self, board, grid_len):
        # Define the size of the board and the size of each cell
        board_size = 450
        cell_size = board_size // grid_len
        line_width = 2
        bold_line_width = 4

        # Create a new image with white background
        img = Image.new('RGB', (board_size, board_size), 'white')
        draw = ImageDraw.Draw(img)

        # Define the font for the numbers
        try:
            if grid_len == 4:
                font = ImageFont.truetype("DejaVuSans.ttf", 48)
            else:
                font = ImageFont.truetype("DejaVuSans.ttf", 33)
        except IOError:
            print("Font not found, using default font")
            font = ImageFont.load_default()

        # Draw the grid lines
        for i in range(grid_len + 1):
            line_weight = bold_line_width if i % int(math.sqrt(grid_len)) == 0 else line_width
            # Vertical lines
            draw.line([(i * cell_size, 0), (i * cell_size, board_size)], fill='black', width=line_weight)
            # Horizontal lines
            draw.line([(0, i * cell_size), (board_size, i * cell_size)], fill='black', width=line_weight)

        # Draw the numbers in the cells
        for row in range(grid_len):
            for col in range(grid_len):
                if board[row][col] != 0:
                    text = str(board[row][col])
                    bbox = draw.textbbox((0, 0), text, font=font)
                    w = bbox[2] - bbox[0]
                    h = bbox[3] - bbox[1]
                    pos = (col * cell_size + (cell_size - w) / 2, row * cell_size + (cell_size - h) / 2)
                    draw.text(pos, text, fill='black', font=font)

        # return img
        return img

    def get_status4simulator(self, player_idx):
        if player_idx >= len(self.scores):
            return None
        return self.scores[player_idx]

    def get_state4simulator(self) -> List[BaseMessageDataType]:
        if self.grid is None:
            return [BaseMessageDataType(data='', type='text')]
        return [BaseMessageDataType(data=self.grid_image, type='image')]

    def get_puzzle_intro4simulator(self) -> List[BaseMessageDataType]:
        puzzle_intro = PUZZLE_INTRO
        return [BaseMessageDataType(data=puzzle_intro, type='text')]