DESCRIPTION = '''You are playing a game name 'exclusivity probes'. There are some number of particles in a force field. By an exclusion principle they must differ from one another by at least k among d dimensions where each dimension is a binary value (for example, up or down spin). If it helps, think of the setting as a d-dimensional hypercube.
Now suppose there are {dimension} dimensions and {num_particles} particles such that any two particles differ in at least {distance} dimensions. Each time, you can probe one position, and then I will response 'yes' if a particle is at position p and 'no' otherwise. Your objective is to find all the positions of {num_particles} particles with as few probes as possible.
For example, if the dimension is 2, the number of particles is 2, and the distance is 1. We can probe the position [0, 0], and if the response is 'yes', we only need one more probe to find the other particle because the particles can be either at locations [0, 0] and [1, 1] or at [0, 1] and [1, 0]. If the response is 'no', we need 3 more probes to find all the particles.
Provide the output in the following format:
Reasoning: ...
Operation: Output one position you want to probe in the format `position = [d1, d2, ..., dn]`, where the length of the list is equal to the number of dimensions, and each value is either 0 or 1.
'''

SIMPLIFIED_DESCRIPTION = None

STATE_TRANSIT_PROMPT = None

CODE_PROMPT = '''You are about to play a game called **Exclusivity Probes**.

Rules
-----
1. You are placed in a d-dimensional binary hypercube (each dimension is 0 or 1).
2. There are a total of `num_particles` hidden particles in the space.
3. Any two particles differ in at least `distance` dimensions (exclusion principle).
4. On each turn, you may **probe** one position by proposing a binary vector of length `dimension`.
5. After probing, you receive feedback:  
   - **"yes"** if a particle exists at the position you probed,  
   - **"no"** otherwise.
6. Your objective is to find **all** `num_particles` with **as few probes as possible**.

Example  
--------
Suppose:
- `dimension = 2`
- `num_particles = 2`
- `distance = 1`

Initially you probe `[0, 0]`.  
- If the answer is **yes**, you know one particle is at `[0, 0]`. You only need a few more probes to find the second.
- If the answer is **no**, you update your hypotheses and continue probing to cover the space while respecting the minimum distance constraint.

Task
----
Implement a Python strategy that, given the current `dimension`, `num_particles`, `distance`, and feedback from previous probe (if any), returns the **next position to probe**.

**Input Format:**  
- `dimension`: an integer representing the number of binary dimensions.  
- `num_particles`: an integer representing the number of hidden particles.  
- `distance`: an integer representing the minimum Hamming distance between any two particles.  
- `guess`: a list of integers (0/1) representing the previous probe made (or `None` if it is the first move).  
- `is_particle`: a boolean. `True` means the previous probe found a particle, `False` otherwise.

**Output Format:**  
- Return a list of integers representing the next position you wish to probe. The list should have length equal to `dimension` and each entry should be either `0` or `1`.

You should also consider the computational efficiency of your program—if it runs for more than 5 minutes, you will lose the game.

Template
----------------------------------------
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum
from abc import abstractmethod

from system.message import Info
from system.message import BaseMessageDataType
from model.strategy_type import StrategyType
from model.base import BaseStrategy


class ExclusivityProbesCustomStrategy:
    def __init__(self, model: BaseStrategy):
        self._model = model
        self.name = self._model.name
        self.history = self._model.history
        self.strategy_type = StrategyType.Custom
    
    def update_model_field(self, field_name: str, value: Any):
        if hasattr(self._model, field_name):
            setattr(self._model, field_name, value)

    def receive_message(self, message: Info) -> Info:
        data = message.message[0].data
        # dimension is integer
        dimension = data['dimension']
        # num_particles is integer indicating how many particles
        num_particles = data['num_particles']
        # distance is integer
        distance = data['distance']
        # prev_guess is a list of integers with dimension equal to the dimension representing the previous probing
        prev_guess = data['guess']
        # is_particle is a bool, True means your previous guess did find a particle
        is_particle = data['is_particle']
        # return a list of integers with length equals to dimension
        next_guess = None
        # TODO: implement your decision logic here

        return Info(
            sender=self.__class__.__name__,
            receiver=message.sender,
            difficulty=message.difficulty,
            message=[BaseMessageDataType(data=next_guess, type='custom')]
        )

Guidelines
----------
* The existing template should not be modified. You can add variables, functions, or classes as needed, for example you may add helper functions to generate the next probe systematically, track known particles, etc.
* You can import additional libraries and assume they are already installed.

Required Output Format
----------------------
Return a single JSON object:

{
  "reasoning": "<your step-by-step explanation>",
  "code": "<only the Python code and the code must be complete that including code in template>"
}

* `reasoning` — concise explanation of how you determined the `next_guess`.
* `code` — complete, syntax-error-free Python implementing the decision logic, with **no** ```python fences or other formatting.
'''

PUZZLE_INTRO = '''Game Description
        
Game: Exclusivity Probes

Overview:
Exclusivity Probes is a strategic puzzle game where you must discover the positions of a set number of particles within a d-dimensional hypercube. The particles are subject to an exclusion principle, meaning they differ from each other by at least a specified distance (k) across the d binary dimensions. Your task is to locate all the particles using the fewest possible probes.

Mechanics:
1. Objective:
- Your goal is to find the exact positions of all particles.
- You can probe one position at a time. If a particle exists at the probed position, the response will be "yes," otherwise, "no."
- The challenge is to find all the particles using as few probes as possible by leveraging the exclusion principle.

2. Conditions:
- The exclusion principle dictates that if a particle is found at one position, the remaining particles must differ by at d dimensions from that position.
- The game ends when you have located all the particles.'''