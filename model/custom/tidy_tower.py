from pydantic import BaseModel
from typing import List, Optional, Tuple, Any
from enum import Enum
from abc import abstractmethod

from system.message import Info
from system.message import BaseMessageDataType
from model.strategy_type import StrategyType
from model.base import BaseStrategy

import heapq

def tidy_tower(cubes: List[str]) -> List[List[int]]:
    N = len(cubes)
    colors = ['R', 'Y', 'B', 'G']
    target_colors = ['R', 'Y', 'B', 'G']
    min_total_moves = float('inf')
    best_moves = []

    # Preprocess cubes to get their orientations
    cube_orientations = []
    for cube in cubes:
        orientations = [cube[i:] + cube[:i] for i in range(4)]
        cube_orientations.append(orientations)

    # Try each target color
    for target_color in target_colors:
        dp = [{} for _ in range(N)]  # dp[i][color_above] = (cost, moves)
        # Base case for the bottom cube
        dp[0] = {}
        for rotation in range(4):
            front_color = cube_orientations[0][rotation][0]
            if front_color == target_color:
                dp[0][cube_orientations[0][rotation][0]] = (rotation, [[0, rotation + 1, 0]])

        # DP computation
        for i in range(1, N):
            dp[i] = {}
            for color_above, (cost_above, moves_above) in dp[i - 1].items():
                # Option 1: Rotate without holding
                for rotation in range(4):
                    front_color = cube_orientations[i][rotation][0]
                    above_color = rotate_color(color_above, rotation)
                    if front_color == target_color:
                        total_cost = cost_above + rotation
                        total_moves = moves_above + [[i, rotation + 1, 0]]
                        key = above_color
                        if key not in dp[i] or dp[i][key][0] > total_cost:
                            dp[i][key] = (total_cost, total_moves)
                # Option 2: Rotate with holding
                for rotation in range(4):
                    front_color = cube_orientations[i][rotation][0]
                    if front_color == target_color:
                        total_cost = cost_above + rotation
                        total_moves = moves_above + [[i, rotation + 1, 1]]
                        key = color_above  # since above cubes are held, color_above remains the same
                        if key not in dp[i] or dp[i][key][0] > total_cost:
                            dp[i][key] = (total_cost, total_moves)

        # Find minimal total cost for this target color
        for color_above, (total_cost, total_moves) in dp[N - 1].items():
            if total_cost < min_total_moves:
                min_total_moves = total_cost
                best_moves = total_moves

    return best_moves

def rotate_color(color: str, rotation: int) -> str:
    colors = ['R', 'Y', 'B', 'G']
    idx = colors.index(color)
    new_idx = (idx + rotation) % 4
    return colors[new_idx]

class TidyTowerCustomStrategy:
    def __init__(self, model: BaseStrategy):
        self._model = model
        self.name = self._model.name
        self.history = self._model.history
        self.strategy_type = StrategyType.Custom
    
    def update_model_field(self, field_name: str, value: Any):
        if hasattr(self._model, field_name):
            setattr(self._model, field_name, value)

    def receive_message(self, message: Info) -> Info:
        tower = message.message[0].data
        
        # Convert single-letter representation to full cube representation
        full_tower = []
        for color in tower:
            if color == 'R':
                full_tower.append('RYBG')
            elif color == 'Y':
                full_tower.append('YBGR')
            elif color == 'B':
                full_tower.append('BGRY')
            elif color == 'G':
                full_tower.append('GRYB')
        
        moves = tidy_tower(full_tower)
        
        # Adjust rotation values to be 1-indexed
        for move in moves:
            move[1] = move[1] -1
        
        return Info(sender='model', receiver='user', message=[BaseMessageDataType(data=moves, type='text')])
