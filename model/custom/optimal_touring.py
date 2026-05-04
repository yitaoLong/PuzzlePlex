from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from abc import abstractmethod

from system.message import Info
from system.message import BaseMessageDataType
from model.strategy_type import StrategyType
from model.base import BaseStrategy

from collections import namedtuple
import random
import math


SiteInfo = namedtuple('SiteInfo', ['site', 'avenue', 'street', 'desiredtime', 'value', 'beginhour', 'endhour'])
Site = namedtuple('Site', ['id', 'avenue', 'street', 'desiredtime', 'value', 'beginhour', 'endhour'])

class OptimalTouringCustomStrategy:
    def __init__(self, model: BaseStrategy):
        self._model = model
        self.name = self._model.name
        self.history = self._model.history
        self.strategy_type = StrategyType.Custom

    def update_model_field(self, field_name: str, value: Any):
        if hasattr(self._model, field_name):
            setattr(self._model, field_name, value)
            
    def receive_message(self, message: Info) -> Info:
        # Extract the data from the message
        sites_data = message.message[0].data
        
        # Adjusted to handle tuple format
        if isinstance(sites_data, tuple):
            # Extract the first element, which should be the data dictionary
            if len(sites_data) >= 1 and isinstance(sites_data[0], dict):
                sites_data_dict = sites_data[0]
            else:
                raise ValueError("The first element of the tuple must be a dictionary of site data.")
        elif isinstance(sites_data, dict):
            sites_data_dict = sites_data
        else:
            raise ValueError(f"Unexpected type for sites_data: {type(sites_data)}")
        
        # Create Site objects
        sites = [Site(id=site_id, **data) for site_id, data in sites_data_dict.items()]
        
        # Apply the Simulated Annealing algorithm
        total_value, tour = self.optimal_touring(sites)
    
        return Info(
            sender=self.__class__.__name__,
            receiver=message.sender,
            difficulty=message.difficulty,
            message=[BaseMessageDataType(data=tour, type='custom')]
        )
    
    def optimal_touring(self, sites: List[Site]) -> Tuple[int, List[int]]:
        T = 1000.0  # Initial temperature
        T_min = 1.0  # Minimum temperature
        alpha = 0.995  # Cooling rate
        max_iterations = 10000

        current_solution = []
        current_value = 0
        best_solution = []
        best_value = 0

        iteration = 0

        while T > T_min and iteration < max_iterations:
            iteration += 1

            new_solution = self.generate_neighbor_solution(current_solution, sites)
            new_value = self.evaluate_solution(new_solution, sites)

            delta = new_value - current_value

            if delta > 0 or random.random() < math.exp(delta / T):
                current_solution = new_solution
                current_value = new_value

                if current_value > best_value:
                    best_solution = current_solution[:]
                    best_value = current_value

            T *= alpha

        return best_value, best_solution

    def generate_neighbor_solution(self, current_solution: List[int], sites: List[Site]) -> List[int]:
        new_solution = current_solution[:]
        action = random.choice(['add', 'remove', 'swap'])
        
        site_ids = [site.id for site in sites]

        if action == 'add':
            available_sites = [site_id for site_id in site_ids if site_id not in current_solution]
            if available_sites:
                site_to_add = random.choice(available_sites)
                insert_position = random.randint(0, len(new_solution))
                new_solution.insert(insert_position, site_to_add)
        elif action == 'remove' and current_solution:
            site_to_remove = random.choice(current_solution)
            new_solution.remove(site_to_remove)
        elif action == 'swap' and len(current_solution) >= 2:
            idx1, idx2 = random.sample(range(len(current_solution)), 2)
            new_solution[idx1], new_solution[idx2] = new_solution[idx2], new_solution[idx1]
        
        return new_solution

    def evaluate_solution(self, tour_site_ids: List[int], sites: List[Site]) -> int:
        site_dict = {site.id: site for site in sites}
        tour_sites = [site_dict.get(site_id) for site_id in tour_site_ids if site_id in site_dict]
        
        if len(tour_sites) != len(tour_site_ids):
            return 0  # Invalid site ID in tour
        
        total_value = 0
        current_time = None
        prev_site = None

        for site in tour_sites:
            if current_time is None:
                current_time = site.beginhour * 60  # Convert hours to minutes
                if current_time + site.desiredtime > site.endhour * 60:
                    return 0  # Cannot spend desired time within visiting hours
                total_value += site.value
                current_time += site.desiredtime  # Update current time after visiting
                prev_site = site
                continue

            travel_time = abs(site.avenue - prev_site.avenue) + abs(site.street - prev_site.street)
            arrival_time = current_time + travel_time

            if arrival_time < site.beginhour * 60 or arrival_time + site.desiredtime > site.endhour * 60:
                return 0  # Cannot arrive during visiting hours or not enough time

            current_time = arrival_time + site.desiredtime
            total_value += site.value
            prev_site = site

        return total_value
