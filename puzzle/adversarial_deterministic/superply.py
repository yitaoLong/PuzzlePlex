from pydantic import BaseModel
from typing import List, Any

from model.base import BaseStrategy
from system.message import Info
from system.message import BaseMessageDataType
from system.message import StateLegality
from system.message import GameStatus

from puzzle.base import BasePuzzle
from prompts.superply import *

import random
import re


class SuperplyPuzzle(BasePuzzle):
    grid: List[List[int]] = None
    prev_move: Any = None
    llm_description_1: str = ''
    llm_description_2: str = ''
    err_1_cnt: int = 0
    err_2_cnt: int = 0
    hints: List[str] = []
    prev_hint: str = ''
    count: int = 0
    winner: int = -1

    def puzzle_generator(self, models: List[BaseStrategy], difficulty: str, one_shot: bool, tot: bool, iterative: bool, simplified_description: bool, legal_candidates: bool, with_history: bool, code_generation: bool, random_seed: Any, output_dir: str) -> List[Info]:
        self.difficulty = difficulty
        self.code_generation = code_generation
        self.output_dir = output_dir

        if random_seed is not None:
            self.rs = random_seed
            random.seed(random_seed)

        self.llm_description_1 = DESCRIPTION      
        self.llm_description_2 = self.llm_description_1

        self.grid = None
        self.prev_move = None
        self.err_1_cnt = 0
        self.err_2_cnt = 0
        self.hints = []
        self.prev_hint = ''
        self.count = 0
        self.winner = -1

        if self.difficulty == 'easy':
            self.grid = [[0 for _ in range(6)] for _ in range(6)]
        elif self.difficulty == 'normal':
            self.grid = [[0 for _ in range(9)] for _ in range(9)]

        self.hints.append(self.generate_hint())

        self.history['setting'] = {'grid_size': len(self.grid)}
        self.history['state'] = []

        message_list: List[Info] = []
        model = models[0]
        if self.code_generation:
            message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=CODE_PROMPT, type='text')], generated_type='code'))
        else:
            if model.strategy_type.value != 'LLM':
                message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=(self.grid, self.hints[-1], 0), type='custom')]))
                self.llm_description_2 += 'Here, you are the second player. You need to wait for the first player to choose a position.\n'
            else:
                self.llm_description_1 += 'Here, you are the first player.'
                self.llm_description_1 += 'The current grid is as follows:\n' + str(self.grid) + '\n'
                self.llm_description_1 += 'The current hint is: ' + self.hints[-1] + '\n'
                self.llm_description_2 += 'Here, you are the second player. You need to wait for the first player to choose a position.\n'
                message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=self.llm_description_1, type='text')]))
                self.llm_description_1 = ''
        
        return message_list

    def state_transition_checker(self, message: Info, response: Info, model: BaseStrategy):
        data = response.message[0].data
        if data is None:
            return message, StateLegality.NONE
        else:
            return message, StateLegality.LEGAL

    def state_transition(self, response: Info, model: BaseStrategy, next_model: Any):
        data = response.message[0].data
        self.prev_move = data

        # check if the selected position is valid
        operation = self.hints[-1].split(' ')[0]
        condition = ' '.join(self.hints[-1].split(' ')[1:])
        # extract the values from the condition and replace the actual values in the condition to v1 and v2
        v1 = None
        v2 = None
        tmp = re.findall(r'\d+', condition)
        if len(tmp) > 0:
            v1 = int(tmp[0])
            condition = condition.replace(str(v1), 'v1')
        if len(tmp) > 1:
            v2 = int(tmp[1])
            condition = condition.replace(str(v2), 'v2')
        is_valid = self.check_position(operation, condition, v1, v2, data)

        updated_desccription = ''
        self.prev_hint = self.hints[-1]
        if is_valid:
            self.grid[data[0]-1][data[1]-1] = self.count + 1
            self.history['state'].append(f'turn: {self.count}, position: {data}, hint: {self.hints[-1]}, correct: True, grid: {self.grid}')

            all_filled = True
            for i in range(len(self.grid)):
                for j in range(len(self.grid[0])):
                    if self.grid[i][j] == 0:
                        all_filled = False
                        break
                if not all_filled:
                    break
            if all_filled:
                self.hints.append('')
            else:
                self.hints.append(self.generate_hint())
            updated_desccription = '''Your opponent has chosen the position {}. This position is valid for the hint. Now the grid becomes {}. The current hint is: {}. Now it is your turn.'''.format(data, str(self.grid), self.hints[-1])
        else:
            self.history['state'].append(f'turn: {self.count}, position: {data}, hint: {self.hints[-1]}, correct: False, grid: {self.grid}')

            if self.count == 0:
                self.err_1_cnt += 1
            else:
                self.err_2_cnt += 1
            updated_desccription = '''Your opponent has chosen the position {}. This position is not valid for the hint. The grid remains the same, which is {}. The current hint is: {}. Now it is your turn.'''.format(data, str(self.grid), self.hints[-1])

        if self.count == 0:
            self.llm_description_2 += updated_desccription
        else:
            self.llm_description_1 += updated_desccription
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
            return Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=(self.grid, self.hints[-1], self.count), type='custom')])

    def game_over_checker(self, model: BaseStrategy):
        if self.err_1_cnt == 15 or self.err_2_cnt == 15:
            return GameStatus.END
        tmp = self.check_path(self.grid)
        if tmp == -1:
            for i in range(len(self.grid)):
                for j in range(len(self.grid[0])):
                    if self.grid[i][j] == 0:
                        return GameStatus.ONGOING
            return GameStatus.END
        else:
            self.winner = tmp
            return GameStatus.END

    def calculate_score(self, game_status: GameStatus, current_player: int):
        if game_status == GameStatus.END:
            if self.err_1_cnt == 15:
                self.scores = ['Lose', 'Win']
                return 1
            elif self.err_2_cnt == 15:
                self.scores = ['Win', 'Lose']
                return 0
            if current_player == 0:
                if self.winner == 0:
                    self.scores = ['Win', 'Lose']
                else:
                    self.scores = ['Lose', 'Win']
            else:
                if self.winner == 1:
                    self.scores = ['Lose', 'Win']
                else:
                    self.scores = ['Win', 'Lose']
            return self.winner
        else:
            if current_player == 0:
                self.scores = ['Lose', 'Win']
            else:
                self.scores = ['Win', 'Lose']
            return 1 - current_player

    def generate_hint(self):
        operations = ['sum', 'product', 'difference']
        conditions = ['is less than v1', 'is greater than v1', 'contains digit v1', 'is even', 'is odd', 'is between v1 and v2, inclusive']

        while True:
            operation = random.choice(operations)
            condition = random.choice(conditions)

            v1 = None
            v2 = None

            if condition == 'is less than v1' or condition == 'is greater than v1':
                v1 = random.randint(0, len(self.grid) * len(self.grid))
            if condition == 'contains digit v1':
                v1 = random.randint(0, 9)
            if condition == 'is between v1 and v2, inclusive':
                v1 = random.randint(0, len(self.grid) * len(self.grid)-1)
                v2 = random.randint(v1+1, len(self.grid) * len(self.grid))

            is_satisfied = self.check_hint(operation, condition, v1, v2)
            if is_satisfied:
                tmp = operation + ' ' + condition
                if v1 is not None:
                    tmp = tmp.replace('v1', str(v1))
                if v2 is not None:
                    tmp = tmp.replace('v2', str(v2))
                return tmp

    def check_hint(self, operation, condition, v1, v2):
        if operation == 'sum':
            if condition == 'is less than v1':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if sum((i+1, j+1)) < v1 and self.grid[i][j] == 0:
                            return True
            elif condition == 'is greater than v1':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if sum((i+1, j+1)) > v1 and self.grid[i][j] == 0:
                            return True
            elif condition == 'contains digit v1':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if str(sum((i+1, j+1))).find(str(v1)) != -1 and self.grid[i][j] == 0:
                            return True
            elif condition == 'is even':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if sum((i+1, j+1)) % 2 == 0 and self.grid[i][j] == 0:
                            return True
            elif condition == 'is odd':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if sum((i+1, j+1)) % 2 != 0 and self.grid[i][j] == 0:
                            return True
            elif condition == 'is between v1 and v2, inclusive':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if v1 <= sum((i+1, j+1)) <= v2 and self.grid[i][j] == 0:
                            return True
        elif operation == 'product':
            if condition == 'is less than v1':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if (i+1)*(j+1) < v1 and self.grid[i][j] == 0:
                            return True
            elif condition == 'is greater than v1':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if (i+1)*(j+1) > v1 and self.grid[i][j] == 0:
                            return True
            elif condition == 'contains digit v1':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if str((i+1)*(j+1)).find(str(v1)) != -1 and self.grid[i][j] == 0:
                            return True
            elif condition == 'is even':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if (i+1)*(j+1) % 2 == 0 and self.grid[i][j] == 0:
                            return True
            elif condition == 'is odd':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if (i+1)*(j+1) % 2 != 0 and self.grid[i][j] == 0:
                            return True
            elif condition == 'is between v1 and v2, inclusive':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if v1 <= (i+1)*(j+1) <= v2 and self.grid[i][j] == 0:
                            return True
        elif operation == 'difference':
            if condition == 'is less than v1':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if abs(i+1-j-1) < v1 and self.grid[i][j] == 0:
                            return True
            elif condition == 'is greater than v1':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if abs(i+1-j-1) > v1 and self.grid[i][j] == 0:
                            return True
            elif condition == 'contains digit v1':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if str(abs(i+1-j-1)).find(str(v1)) != -1 and self.grid[i][j] == 0:
                            return True
            elif condition == 'is even':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if abs(i+1-j-1) % 2 == 0 and self.grid[i][j] == 0:
                            return True
            elif condition == 'is odd':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if abs(i+1-j-1) % 2 != 0 and self.grid[i][j] == 0:
                            return True
            elif condition == 'is between v1 and v2, inclusive':
                for i in range(len(self.grid)):
                    for j in range(len(self.grid[0])):
                        if v1 <= abs(i+1-j-1) <= v2 and self.grid[i][j] == 0:
                            return True
        return False

    def check_position(self, operation, condition, v1, v2, data):
        try:
            if operation == 'sum':
                if condition == 'is less than v1':
                    if sum((data[0], data[1])) < v1 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
                elif condition == 'is greater than v1':
                    if sum((data[0], data[1])) > v1 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
                elif condition == 'contains digit v1':
                    if str(sum((data[0], data[1]))).find(str(v1)) != -1 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
                elif condition == 'is even':
                    if sum((data[0], data[1])) % 2 == 0 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
                elif condition == 'is odd':
                    if sum((data[0], data[1])) % 2 != 0 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
                elif condition == 'is between v1 and v2, inclusive':
                    if v1 <= sum((data[0], data[1])) <= v2 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
            elif operation == 'product':
                if condition == 'is less than v1':
                    if (data[0])*(data[1]) < v1 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
                elif condition == 'is greater than v1':
                    if (data[0])*(data[1]) > v1 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
                elif condition == 'contains digit v1':
                    if str((data[0])*(data[1])).find(str(v1)) != -1 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
                elif condition == 'is even':
                    if (data[0])*(data[1]) % 2 == 0 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
                elif condition == 'is odd':
                    if (data[0])*(data[1]) % 2 != 0 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
                elif condition == 'is between v1 and v2, inclusive':
                    if v1 <= (data[0])*(data[1]) <= v2 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
            elif operation == 'difference':
                if condition == 'is less than v1':
                    if abs(data[0]-data[1]) < v1 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
                elif condition == 'is greater than v1':
                    if abs(data[0]-data[1]) > v1 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
                elif condition == 'contains digit v1':
                    if str(abs(data[0]-data[1])).find(str(v1)) != -1 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
                elif condition == 'is even':
                    if abs(data[0]-data[1]) % 2 == 0 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
                elif condition == 'is odd':
                    if abs(data[0]-data[1]) % 2 != 0 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
                elif condition == 'is between v1 and v2, inclusive':
                    if v1 <= abs(data[0]-data[1]) <= v2 and self.grid[data[0]-1][data[1]-1] == 0:
                        return True
        except:
            return False

    def check_path(self, grid):
        def dfs(x, y, value, visited, is_horizontal):
            if (is_horizontal and y == len(self.grid)-1) or (not is_horizontal and x == len(self.grid)-1):
                return True
            
            visited.add((x, y))
            directions = [(0,1), (1,0), (0,-1), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < len(self.grid) and 0 <= ny < len(self.grid) and grid[nx][ny] == value and (nx, ny) not in visited:
                    if dfs(nx, ny, value, visited, is_horizontal):
                        return True
            
            return False

        # Check for horizontal path (value 1)
        for i in range(len(self.grid)):
            if grid[i][0] == 1:
                if dfs(i, 0, 1, set(), True):
                    return 0

        # Check for vertical path (value 2)
        for j in range(len(self.grid)):
            if grid[0][j] == 2:
                if dfs(0, j, 2, set(), False):
                    return 1
        return -1

    def get_status4simulator(self, player_idx):
        if player_idx >= len(self.scores):
            return None
        return self.scores[player_idx]

    def get_state4simulator(self) -> List[BaseMessageDataType]:
        if self.prev_hint == '':
            return [BaseMessageDataType(data='Game Starts', type='text')]
        state = ''
        state += 'Current hint: ' + self.prev_hint + '\n\n'
        state += 'Position: ' + str(self.prev_move) + '\n\n'
        state += 'Grid becomes:\n'
        for row in self.grid:
            state += str(row) + '\n'
        return [BaseMessageDataType(data=state, type='text')]

    def get_puzzle_intro4simulator(self) -> List[BaseMessageDataType]:
        puzzle_intro = PUZZLE_INTRO
        return [BaseMessageDataType(data=puzzle_intro, type='text')]