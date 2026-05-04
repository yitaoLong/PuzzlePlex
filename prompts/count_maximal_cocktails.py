DESCRIPTION_EASY = '''Your task it to solve a puzzle named 'Count Maximal Cocktails'. Orphan diseases affect very few people, making the development of specific drugs challenging. To treat these diseases, a combination of drugs designed for other related conditions is often used. However, combining drugs can lead to harmful interactions. If no harmful interactions are present, combining the drugs may result in a synergistic effect, potentially benefiting the patient.

In this game, drugs are represented as nodes in a graph, and harmful interactions between drugs are represented as edges between nodes. The objective is to identify all maximal drug combinations, known as maximal cocktails, which correspond to the maximum independent sets in the graph. Players will explore how the addition of new interactions affects the number of maximal cocktails.

The current drug list is {nodes_list}, and the bad interaction list is {edges_list}. Each item in the interaction list is a tuple, and the two values in a tuple indicate that these two drugs have a bad interaction. what are the number of maximal cocktails? 
For example, if the drug list is [1, 2, 3, 4] and the bad interaction list is [(1, 2)], the maximal cocktails are [1, 3, 4] and [2, 3, 4], so the number of maximal cocktails is 2.
Provide the output in the following format:
Reasoning: ...
Operation: Output the maximal cocktails in the format `maximal_cocktails = int`.
'''

DESCRIPTION_NORMAL = '''Your task it to solve a puzzle named 'Count Maximal Cocktails'. Orphan diseases affect very few people, making the development of specific drugs challenging. To treat these diseases, a combination of drugs designed for other related conditions is often used. However, combining drugs can lead to harmful interactions. If no harmful interactions are present, combining the drugs may result in a synergistic effect, potentially benefiting the patient.

In this game, drugs are represented as nodes in a graph, and harmful interactions between drugs are represented as edges between nodes. The objective is to identify all maximal drug combinations, known as maximal cocktails, which correspond to the maximum independent sets in the graph. Players will explore how the addition of new interactions affects the number of maximal cocktails.
For example, if the drug list is [1, 2, 3, 4] and the bad interaction list is [(1, 2)], the maximal cocktails are [1, 3, 4] and [2, 3, 4], thus maximal_cocktails=[[1, 3, 4], [2, 3, 4]].
The current drug list is {nodes_list}, and the bad interaction list is {edges_list}. Each item in the interaction list is a tuple, and the two values in a tuple indicate that these two drugs have a bad interaction. what are the maximal cocktails? Output all the maximal cocktails.
Provide the output in the following format:
Reasoning: ...
Operation: Output the maximal cocktails in the format `maximal_cocktails = [[int], [int], ...]`.
'''

SIMPLIFIED_DESCRIPTION = None

STATE_TRANSIT_PROMPT = None

CODE_PROMPT = '''You are about to play a game called **Count Maximal Cocktails**.

Rules
-----
1. In this game, drugs are represented as nodes in a graph.
2. Harmful interactions between drugs are represented as edges connecting nodes.
3. A **cocktail** is a set of drugs with **no harmful interactions** among them.
4. A **maximal cocktail** is a cocktail where **no more drugs can be added** without introducing a harmful interaction.
5. In the **easy level**, you need to calculate **the number of maximal cocktails**.
6. In the **normal level**, you need to **list all maximal cocktails** explicitly.

Example  
--------
Drugs = [1, 2, 3, 4]  
Bad Interactions = [(1, 2)]

- Valid maximal cocktails are:
  - [1, 3, 4]
  - [2, 3, 4]

So:
- In **easy level**, the number of maximal cocktails is **2**.
- In **normal level**, the maximal cocktails are **[[1, 3, 4], [2, 3, 4]]**.

Task
----
Implement a Python strategy that, given the current `nodes_list` and `edges_list`, returns the correct result based on difficulty level.

**Input Format:**  
- `nodes_list`: a list of integers, representing the drugs.  
- `edges_list`: a list of tuples, where each tuple (u, v) means drugs `u` and `v` have a harmful interaction.

**Output Format:**  
- If difficulty is `'easy'`: Return an integer, the number of maximal cocktails.  
- If difficulty is `'normal'`: Return a list of lists, each inner list is a maximal cocktail.

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


class CountMaximalCocktailsCustomStrategy:
    def __init__(self, model: BaseStrategy):
        self._model = model
        self.name = self._model.name
        self.history = self._model.history
        self.strategy_type = StrategyType.SMT
    
    def update_model_field(self, field_name: str, value: Any):
        if hasattr(self._model, field_name):
            setattr(self._model, field_name, value)

    def receive_message(self, message: Info) -> Info:
        data = message.message[0].data
        # nodes_list is a list of nodes in integer
        nodes_list = data['nodes']
        # edges_list is a list of tuple, and the two values in tuple are integer means there is an edge between these two nodes
        edges_list = data['edges']
        
        if message.difficulty == 'easy':
            # return the number of maximal cocktails in integer
            num_maximal_cocktails = None
        elif message.difficulty == 'normal':
            # return the maximal cocktails in a list of list, and each inner list means a disjoint cocktail list in integer
            maximal_cocktails = None

        return Info(
            sender=self.__class__.__name__,
            receiver=message.sender,
            difficulty=message.difficulty,
            message=[BaseMessageDataType(data=num_maximal_cocktails if message.difficulty == 'easy' else maximal_cocktails, type='custom')]
        )

Guidelines
----------
* The existing template should not be modified. You can add variables, functions, or classes as needed, for example you may add helper variables or logic to track card usage, past moves, etc.
* You can import additional libraries and assume any additional libraries are already installed. 

Required Output Format
----------------------
Return a single JSON object:

{
  "reasoning": "<your step-by-step explanation>",
  "code": "<only the Python code and the code must be complete that including code in template>"
}

* `reasoning` — concise explanation of how you determined the answer.
* `code` — complete, syntax-error-free Python implementing the decision logic, with **no** ```python fences or other formatting.
'''

PUZZLE_INTRO = '''Game Description
        
Game: Count Maximal Cocktails

Overview:
Players are tasked with finding all possible maximal drug combinations, known as maximal cocktails, that do not involve harmful interactions. These cocktails are represented as maximum independent sets in a graph where:
- Nodes represent drugs.
- Edges represent harmful interactions between two drugs.
The objective is to determine the number of maximal cocktails/identify all maximal cocktails given a list of drugs and a list of harmful interactions between them.

Mechanics:

1. Graph Representation:
- Nodes: Each drug is a node in the graph.
- Edges: Each harmful interaction between two drugs is an edge connecting two nodes.

2. Objective:
- Identify all maximal cocktails, which are the largest sets of nodes (drugs) that can be combined without any edges (harmful interactions) between them.

3. Conditions:
- A maximal cocktail is a set of drugs where no additional drugs can be added without causing a harmful interaction.
- The number of maximal cocktails is the total number of such sets.'''