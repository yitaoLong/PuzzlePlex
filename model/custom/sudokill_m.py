from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from abc import abstractmethod

from system.message import Info
from system.message import BaseMessageDataType
from model.strategy_type import StrategyType
from model.base import BaseStrategy


class SudoKillMCustomStrategy:
    def __init__(self, model: BaseStrategy):
        self._model = model
        self.name = self._model.name
        self.history = self._model.history
        self.strategy_type = StrategyType.Custom
    
    def update_model_field(self, field_name: str, value: Any):
        if hasattr(self._model, field_name):
            setattr(self._model, field_name, value)

    def receive_message(self, message: Info) -> Info:
        if message.difficulty == 'easy':
            # randomly move
            grid = message.message[0].data[1]
            prev_move = message.message[0].data[0]
            # get valid moves
            valid_moves = self.get_valid_moves(grid, prev_move)

            if len(valid_moves) == 0:
                return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=None, type='custom')])
            else:
                # Choose a valid move
                for move in valid_moves:
                    row, col = move
                    for value in range(1, len(grid) + 1):
                        if self.is_valid_move(grid, row, col, value):
                            data = [(row, col), value]
                            return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=data, type='custom')])
                # No valid move found
                return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=None, type='custom')])
        elif message.difficulty == 'normal':
            # backtracking to find if there is a move that will lead to a win
            
            grid = message.message[0].data[1]
            prev_move = message.message[0].data[0]
            # get valid moves
            valid_moves = self.get_valid_moves(grid, prev_move)

            if len(valid_moves) == 0:
                return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=None, type='custom')])
            
            count = 0
            for i in range(len(grid)):
                for j in range(len(grid[0])):
                    if grid[i][j] == 0:
                        count += 1
            if count <= 40:
                # find all legal values for each empty cell
                legal_values = {}
                for i in range(len(grid)):
                    for j in range(len(grid[0])):
                        if grid[i][j] == 0:
                            legal_values[(i, j)] = []
                            for value in range(1, len(grid) + 1):
                                if self.is_valid_move(grid, i, j, value):
                                    legal_values[(i, j)].append(value)
                
                for move in valid_moves:
                    next_valid_moves = self.get_valid_moves(grid, [move, 0])
                    for value in legal_values[move]:
                        is_good = True
                        for tmp_move in next_valid_moves:
                            for tmp_value in legal_values[tmp_move]:
                                if value != tmp_value:
                                    is_good = False
                                    break
                            if not is_good:
                                break
                        if is_good:
                            data = [move, value]
                            return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=data, type='custom')])

            # Choose a valid move
            for move in valid_moves:
                row, col = move
                for value in range(1, len(grid) + 1):
                    if self.is_valid_move(grid, row, col, value):
                        data = [(row, col), value]
                        return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=data, type='custom')])
            # No valid move found
            return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=None, type='custom')])

    def is_valid_move(self, board, row, col, value):
        # Check row constraint
        if value in board[row]:
            return False

        # Check column constraint
        if value in [board[i][col] for i in range(len(board))]:
            return False

        # Check box constraint
        box_row = (row // int(len(board) ** 0.5)) * int(len(board) ** 0.5)
        box_col = (col // int(len(board) ** 0.5)) * int(len(board) ** 0.5)
        if value in [board[box_row + i // int(len(board) ** 0.5)][box_col + i % int(len(board) ** 0.5)] for i in range(len(board))]:
            return False
        return True
    
    def get_valid_moves(self, grid, prev_move):
        valid_moves = []
        if prev_move is None:
            for i in range(len(grid)):
                for j in range(len(grid[0])):
                    if grid[i][j] == 0:
                        valid_moves.append((i, j))
        else:
            for i in range(len(grid)):
                if grid[prev_move[0][0]][i] == 0:
                    valid_moves.append((prev_move[0][0], i))
                if grid[i][prev_move[0][1]] == 0:
                    valid_moves.append((i, prev_move[0][1]))
            if len(valid_moves) == 0:
                for i in range(len(grid)):
                    for j in range(len(grid[0])):
                        if grid[i][j] == 0:
                            valid_moves.append((i, j))
        return valid_moves