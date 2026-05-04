DESCRIPTION = '''Your task is to solve a puzzle called "Optimal Touring".

You are given a list of tourist sites, each with:
- A location defined by street and avenue coordinates.
- A fixed desired visiting time (in minutes) that must be spent at the site.
- A value representing the reward or importance of visiting the site.
- Visiting hours (start and end times) on a particular day.

You want to visit as many valuable sites as possible within a single day, subject to the following constraints:
- You can start at any site.
- The total duration includes:
  - The visiting time at each site.
  - The travel time between consecutive sites, defined as the Manhattan distance (i.e., the sum of the differences in street and avenue coordinates).
- You can only visit a site within its allowed time window.

Your goal:
Find the optimal sequence of site visits in one day to maximize the total value.

Here is an example of the input data:
site  avenue  street  desired_time  value  begin_hour  end_hour
1     50      96      114           3         6           12
2     8       23      190           186       9           17
3     88      69      218           3         9           12
4     0       95      101           86        6           12
5     1       48      192           199       5           12
In this example, you can start visit cite 5 at 5:00, then go to site 2, then the hour is after 12:00, and the value you get is 199 + 186 = 385.

Now the game starts! The site data is {site_data}.

Please provide your output in the following format:

Reasoning: Explain your reasoning process to determine the optimal sequence of site visits.

Operation: Provide the selected site sequence as a list:
List[int] = [site1, site2, site3, ...]'''

DESCRIPTION_ITERATIVE = '''Your task is to solve a puzzle called "Optimal Touring".

You are given a list of tourist sites, each with:
- A location defined by street and avenue coordinates.
- A fixed desired visiting time (in minutes) that must be spent at the site.
- A value representing the reward or importance of visiting the site.
- Visiting hours (start and end times) on a particular day.

You want to visit as many valuable sites as possible within a single day, subject to the following constraints:
- You can start at any site.
- The total duration includes:
  - The visiting time at each site.
  - The travel time between consecutive sites, defined as the Manhattan distance (i.e., the sum of the differences in street and avenue coordinates).
- You can only visit a site within its allowed time window.

Your goal:
Find the optimal sequence of site visits in one day to maximize the total value.

Here is an example of the input data:
site  avenue  street  desired_time  value  begin_hour  end_hour
1     50      96      114           3         6           12
2     8       23      190           186       9           17
3     88      69      218           3         9           12
4     0       95      101           86        6           12
5     1       48      192           199       5           12
In this example, you can start visit cite 5 at 5:00, then go to site 2, then the hour is after 12:00, and the value you get is 199 + 186 = 385.

Now the game starts! The site data is {site_data}. Please solve it in iterative way that each time output one site you want to visit.

Provide the output in the following format:
Reasoning: Explain the reasoning to visit the site.
Operation: output the list in the format of `List[int] = [the site number you want to visit]`, please note that output only one site number in the list.
'''

CODE_PROMPT = '''You are about to play a game called **Optimal Touring**.

Rules
-----
1. You are given a list of tourist sites. Each site has:
   - Avenue and street coordinates.
   - A desired visiting time (in minutes).
   - A reward value.
   - An available visiting window (start hour and end hour).
2. You can start your tour at any site.
3. The total duration includes:
   - The visiting time at each site.
   - The travel time between consecutive sites, measured by Manhattan distance (sum of absolute differences of avenues and streets).
4. You can only visit a site during its allowed visiting hours.
5. You want to maximize the total value collected in a single day.

Example  
--------
Here is an example of the site data:

| site | avenue | street | desired_time | value | begin_hour | end_hour |
|-----:|-------:|-------:|-------------:|------:|-----------:|---------:|
| 1    | 50     | 96     | 114          | 3     | 6          | 12       |
| 2    | 8      | 23     | 190          | 186   | 9          | 17       |
| 3    | 88     | 69     | 218          | 3     | 9          | 12       |
| 4    | 0      | 95     | 101          | 86    | 6          | 12       |
| 5    | 1      | 48     | 192          | 199   | 5          | 12       |

In this example, you can start by visiting site 5 at 5:00, then visit site 2. After that, the time will exceed 12:00, making other visits impossible. The total value you obtain is 199 + 186 = 385.

Task
----
Implement a Python strategy that, given the current `sites_data`, determines the sequence of sites to visit to maximize the total value collected.

**Input Format:**  
- `sites_data`: a dictionary where:
  - Key: int (site id).
  - Value: dict containing:
    - `'avenue'`: int
    - `'street'`: int
    - `'desiredtime'`: int (time needed at the site)
    - `'value'`: int (reward value)
    - `'beginhour'`: int (opening hour)
    - `'endhour'`: int (closing hour)

**Output Format:**  
- Return a list of integers representing the ordered sequence of site ids you will visit.

You should also consider the computational efficiency of your program—if it runs for more than 5 minutes, you will lose the game.

Template
----------------------------------------
from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from abc import abstractmethod

from system.message import Info
from system.message import BaseMessageDataType
from model.strategy_type import StrategyType
from model.base import BaseStrategy

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
        # sites_data is a dict: key=int (site id), value=dict with keys ['avenue', 'street', 'desiredtime', 'value', 'beginhour', 'endhour']
        sites_data = message.message[0].data[0]
        # return data: list of integers representing the visiting order
        visited_sites = None
        # TODO: implement your decision logic here
        return Info(
            sender=self.__class__.__name__,
            receiver=message.sender,
            difficulty=message.difficulty,
            message=[BaseMessageDataType(data=visited_sites, type='custom')]
        )

Guidelines
----------
* The existing template should not be modified. You may add helper functions or variables.
* You can import additional libraries if necessary. Assume all libraries are pre-installed.

Required Output Format
----------------------
Return a single JSON object:

{
  "reasoning": "<your step-by-step explanation>",
  "code": "<only the Python code and the code must be complete that including code in template>"
}

* `reasoning` — a concise explanation of how you determined `visited_sites`.
* `code` — complete, syntax-error-free Python implementing the decision logic, with **no** ```python fences or other formatting.
'''

PUZZLE_INTRO = '''Game Description
        
Game: Optimal Touring

Overview:
Players are tasked with finding the optimal tour of sites, ensuring the maximum value is visited within the given time constraints.

Mechanics:

1. Graph Representation:
- Nodes: Each site is a node in the graph.
- Edges: The time taken to travel between two sites is calculated as the sum of the absolute differences in their avenue and street coordinates.

2. Time Constraints:
- Each site has a specific visiting time during the day.
- The total time for any site visit must not exceed the site's end hour multiplied by 60 minutes.

3. Tour Planning:
- Players alternate selecting the next site to visit, ensuring the total time does not exceed the site's end hour multiplied by 60 minutes.
- The goal is to maximize the total value of the visited sites.

'''