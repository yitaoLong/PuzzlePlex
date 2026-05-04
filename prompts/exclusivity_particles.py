DESCRIPTION = '''There are some particles in a force field. By an exclusion principle, they must differ from one another by at least k in d dimensions, where each dimension is binary (for example, up or down spin). If it helps, think of the setting as a d-dimensional hypercube.
Now consider a two-player game. Suppose there are d dimensions, such that any two particles differ in at least k dimensions. The two players take turns adding particles. The first player places a particle, and then the second player adds another, and so on. The game ends when a player cannot place a particle that satisfies the condition, and that player loses.
Please note that the way of computing the distance is the sum of the differences in each dimension. For example, the distance between [0, 0] and [1, 1] is 2.
For instance, if the dimension is 3 and the required distance is 2, and you are the first player, you could place the first particle at [0, 0, 0]. The second player could then place the second particle at [0, 1, 1]. If you place the third particle at [1, 0, 1], the second player cannot place a fourth particle that satisfies the condition and would lose.

Now the game starts and there are {dimension} dimensions, such that any two particles differ in at least {distance} dimensions. 

Provide the output in the following format:
Reasoning: ...
Operation: Output the position of a particle in the format `particle = [d1, d2, ..., dn]`, where the length of the list is equal to the number of dimensions, and each value is either 0 or 1.
''' 

SIMPLIFIED_DESCRIPTION = None

STATE_TRANSIT_PROMPT = '''Your opponent placed a particle at {particle}. Now it is your turn. Please make your move in the required format.'''

CODE_PROMPT = '''You are about to play a game called **Exclusivity Particles** against an opponent.

Rules  
-----
1. The space is a **d-dimensional binary hypercube**, where each coordinate is either 0 or 1.  
2. Players take turns placing particles at binary points in this space (e.g., `[0, 1, 0, 1]`).  
3. A new particle may only be placed if it differs from *all previously placed particles* in **at least k dimensions**.  
4. Distance between two particles is defined as the **Hamming distance**—the number of coordinates in which they differ.  
5. The game ends when a player cannot make a legal move. That player loses.  

Example  
--------
Suppose `dimension = 3` and `distance = 2`. You go first.  
• First player places `[0, 0, 0]`.  
• Second player places `[0, 1, 1]` (differs by 2 from first).  
• First player places `[1, 0, 1]` (differs by ≥2 from both).  
• Now the second player cannot place any new particle that differs by at least 2 from all existing particles, and loses.  

Task  
----
Implement a Python strategy that, given the current list of placed `particles`, the `dimension`, and the required Hamming `distance`, returns the next valid particle to place.

**Input Format:**  
- `dimension`: an integer representing the number of binary dimensions.  
- `distance`: an integer representing the minimum required Hamming distance between any pair of particles.  
- `particles`: a list of lists. Each inner list is a binary list of length equal to `dimension`, representing an already placed particle.

**Output Format:**  
Your return value must be a **list of binary numbers (0 or 1)**, and the **length of this list must be equal to the given `dimension`**.  
If no such valid particle exists, return `None`.

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

class ExclusivityParticlesCustomStrategy:  
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
        # the dimension  
        dimension = data['dimension']  
        # the distance  
        distance = data['distance']  
        # a list containing all previously placed particles  
        cnt_particles = data['particles']  

        next_particle = None  
        # TODO: implement your decision logic here  

        return Info(  
            sender=self.__class__.__name__,  
            receiver=message.sender,  
            difficulty=message.difficulty,  
            message=[BaseMessageDataType(data=next_particle, type='custom')]  
        )  

Guidelines  
----------
* The existing template should not be modified. You may add helper functions, variables, or logic to explore the hypercube efficiently.  
* You can import additional libraries and assume any additional libraries are already installed. 

Required Output Format  
----------------------
Return a single JSON object:

{  
  "reasoning": "<your step-by-step explanation>",  
  "code": "<only the Python code and the code must be complete that including code in template>"  
}

* `reasoning` — concise explanation of how your strategy selects a valid next particle.  
* `code` — complete, syntax-error-free Python implementing the decision logic, with **no** ```python fences or other formatting.
'''

PUZZLE_INTRO = '''Game Description
        
Game: Exclusivity Particles
        
Overview:
In this game, two players take turns placing particles in a force field within a d-dimensional hypercube. The particles must differ by at least a specified distance (k) in terms of dimensions. The game ends when a player can no longer place a valid particle that satisfies the exclusion condition, causing that player to lose.

Mechanics:
1. Objective:
- Players alternate turns, placing a particle in the d-dimensional space.
- The particle's position must differ from all previously placed particles by at least the specified distance in terms of dimensions.
- The game continues until one player cannot place a valid particle that satisfies the distance condition. That player loses.

2. Conditions:
- The distance between two particles is computed as the sum of the differences in each dimension (e.g., the distance between [0, 0] and [1, 1] is 2).
- Players must ensure that each new particle satisfies the required distance from all previously placed particles.'''