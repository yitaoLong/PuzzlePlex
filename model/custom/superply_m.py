from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from abc import abstractmethod

from system.message import Info
from system.message import BaseMessageDataType
from model.strategy_type import StrategyType
from model.base import BaseStrategy

import heapq
import copy
import re


class SuperplyMCustomStrategy:
    def __init__(self, model: BaseStrategy):
        self._model = model
        self.name = self._model.name
        self.history = self._model.history
        self.strategy_type = StrategyType.Custom
        self.current_grid = None
    
    def update_model_field(self, field_name: str, value: Any):
        if hasattr(self._model, field_name):
            setattr(self._model, field_name, value)

    def receive_message(self, message: Info) -> Info:
        self.current_grid = message.message[0].data[0]
        current_hint = message.message[0].data[1]
        player_idx = message.message[0].data[2]

        operation = current_hint.split(' ')[0]
        condition = ' '.join(current_hint.split(' ')[1:])
        v1 = None
        v2 = None
        tmp = re.findall(r'\d+', condition)
        if len(tmp) > 0:
            v1 = int(tmp[0])
            condition = condition.replace(str(v1), 'v1')
        if len(tmp) > 1:
            v2 = int(tmp[1])
            condition = condition.replace(str(v2), 'v2')

        if message.difficulty == 'easy':
            res = None
            for i in range(len(self.current_grid)):
                for j in range(len(self.current_grid[0])):
                    if self.current_grid[i][j] == 0:
                        is_valid = self.check_position(operation, condition, v1, v2, (i+1, j+1))
                        if is_valid:
                            res = (i+1, j+1)
                            break
                if res is not None:
                    break
            return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=res, type='custom')])
        elif message.difficulty == 'normal':
            tmp_grid = copy.deepcopy(self.current_grid)
            for i in range(len(self.current_grid)):
                for j in range(len(self.current_grid[0])):
                    if self.current_grid[i][j] == 0:
                        is_valid = self.check_position(operation, condition, v1, v2, (i+1, j+1))
                        if is_valid:
                            tmp_grid[i][j] = player_idx + 1

            tmp_path = self.find_optimal_path(tmp_grid, player_idx + 1)

            res = None
            for i, j in tmp_path:
                if self.current_grid[i][j] == 0 and tmp_grid[i][j] == player_idx + 1:
                    return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=(i+1, j+1), type='custom')])

            if res is None:
                for i in range(len(self.current_grid)):
                    for j in range(len(self.current_grid[0])):
                        if self.current_grid[i][j] == 0:
                            is_valid = self.check_position(operation, condition, v1, v2, (i+1, j+1))
                            if is_valid:
                                res = (i+1, j+1)
                                break
                    if res is not None:
                        break
                return Info(sender=self.__class__.__name__, receiver=message.sender, difficulty=message.difficulty, message=[BaseMessageDataType(data=res, type='custom')])

    def check_position(self, operation, condition, v1, v2, data):
        if operation == 'sum':
            if condition == 'is less than v1':
                if sum((data[0], data[1])) < v1 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
            elif condition == 'is greater than v1':
                if sum((data[0], data[1])) > v1 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
            elif condition == 'contains digit v1':
                if str(sum((data[0], data[1]))).find(str(v1)) != -1 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
            elif condition == 'is even':
                if sum((data[0], data[1])) % 2 == 0 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
            elif condition == 'is odd':
                if sum((data[0], data[1])) % 2 != 0 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
            elif condition == 'is between v1 and v2, inclusive':
                if v1 <= sum((data[0], data[1])) <= v2 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
        elif operation == 'product':
            if condition == 'is less than v1':
                if (data[0])*(data[1]) < v1 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
            elif condition == 'is greater than v1':
                if (data[0])*(data[1]) > v1 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
            elif condition == 'contains digit v1':
                if str((data[0])*(data[1])).find(str(v1)) != -1 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
            elif condition == 'is even':
                if (data[0])*(data[1]) % 2 == 0 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
            elif condition == 'is odd':
                if (data[0])*(data[1]) % 2 != 0 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
            elif condition == 'is between v1 and v2, inclusive':
                if v1 <= (data[0])*(data[1]) <= v2 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
        elif operation == 'difference':
            if condition == 'is less than v1':
                if abs(data[0]-data[1]) < v1 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
            elif condition == 'is greater than v1':
                if abs(data[0]-data[1]) > v1 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
            elif condition == 'contains digit v1':
                if str(abs(data[0]-data[1])).find(str(v1)) != -1 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
            elif condition == 'is even':
                if abs(data[0]-data[1]) % 2 == 0 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
            elif condition == 'is odd':
                if abs(data[0]-data[1]) % 2 != 0 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
            elif condition == 'is between v1 and v2, inclusive':
                if v1 <= abs(data[0]-data[1]) <= v2 and self.current_grid[data[0]-1][data[1]-1] == 0:
                    return True
    
    def find_optimal_path(self, grid, player_idx):
        rows, cols = len(grid), len(grid[0])

        if player_idx == 1:
            start_points = [(i, 0) for i in range(rows) if grid[i][0] in (0, player_idx)]
            end_points = [(i, cols-1) for i in range(rows) if grid[i][cols-1] in (0, player_idx)]
        else:
            start_points = [(0, i) for i in range(cols) if grid[0][i] in (0, player_idx)]
            end_points = [(rows-1, i) for i in range(cols) if grid[rows-1][i] in (0, player_idx)]
        
        def is_valid(x, y):
            return 0 <= x < rows and 0 <= y < cols and grid[x][y] in (0, player_idx)
        
        def get_neighbors(x, y):
            directions = [(0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (-1,0), (-1,1)]
            return [(x+dx, y+dy) for dx, dy in directions if is_valid(x+dx, y+dy)]
        
        def heuristic(x, y):
            if player_idx == 1:
                return cols - 1 - y
            else:
                return rows - 1 - x
        
        def reconstruct_path(came_from, current):
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]
        
        best_path = None
        max_visited = -1
        
        for start in start_points:
            for end in end_points:
                open_set = [(0, start)]
                came_from = {}
                g_score = {start: 0}
                f_score = {start: heuristic(*start)}
                visited_count = {start: 1 if grid[start[0]][start[1]] == player_idx else 0}
                
                while open_set:
                    _, current = heapq.heappop(open_set)
                    
                    if current == end:
                        path = reconstruct_path(came_from, current)
                        if visited_count[current] > max_visited:
                            max_visited = visited_count[current]
                            best_path = path
                        break
                    
                    for neighbor in get_neighbors(*current):
                        tentative_g_score = g_score[current] + 1
                        
                        if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                            came_from[neighbor] = current
                            g_score[neighbor] = tentative_g_score
                            f_score[neighbor] = g_score[neighbor] + heuristic(*neighbor)
                            visited_count[neighbor] = visited_count[current] + (1 if grid[neighbor[0]][neighbor[1]] == player_idx else 0)
                            heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return best_path