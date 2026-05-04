DESCRIPTION = '''Orphan diseases affect very few people, making the development of specific drugs challenging. To treat these diseases, a combination of drugs designed for other related conditions is often used. However, combining drugs can lead to harmful interactions. If no harmful interactions are present, combining the drugs may result in a synergistic effect, potentially benefiting the patient.

There is a two-player game named 'Max Maximal Cocktails'. In this game, drugs are represented as nodes in a graph, and harmful interactions between drugs are represented as edges between nodes. Based on the edges, we can identify all maximal drug combinations, known as maximal cocktails, which correspond to the maximum independent sets in the graph. And we can explore how the addition of new interactions affects the number of maximal cocktails.

We will give a node list, and then each player plays in turn by adding one edge. The first player whose edge decreases the number of maximal cocktails loses. The edge should be in the format of (node1, node2), where node1 and node2 are two nodes in the list.
For example, if the list is [1, 2, 3], and you are the first player, you can add the edge (1, 2), then the number of maximal cocktails is 2, which is larger than the number of maximal cocktails without the edge (1, 2), which is 1. So this addition is legal. But if your opponent adds the edge (2, 3) after you add the edge (1, 2), then the number of maximal cocktails is 3, which is also legal. After that, you will lose since you cannot add any edge to increase the number of maximal cocktails.

Now the game starts and the node list is {nodes}.

Provide the output in the following format:
Reasoning: ...
Operation: Output the adding edge in the format `edge = (node1, node2)`.
'''

SIMPLIFIED_DESCRIPTION = None

STATE_TRANSIT_PROMPT = "The edge added by your opponent is {data}, which makes the number of maximal cocktails become {new_maximal_cocktails}. Now it's your turn to add an edge.\n"

CODE_PROMPT = '''You are about to play a game called **Max Maximal Cocktails** against an opponent.

Rules  
-----
1. Drugs are represented as nodes in a graph.  
2. Harmful interactions are represented by undirected edges between nodes.  
3. A *cocktail* is a maximal independent set of the graph (i.e., a set of drugs such that no two interact, and no more drugs can be added without causing an interaction).  
4. Initially, the graph has no edges (no harmful interactions).  
5. Players take turns adding a single edge between two nodes.  
6. A move is **legal** only if the number of maximal cocktails **does not decrease** after adding the edge.  
7. The first player to make a move that decreases the number of maximal cocktails **loses**.  

Example  
--------
Given nodes = [1, 2, 3], initial graph has 1 maximal cocktail: [1, 2, 3].  
• Player 1 adds edge (1, 2) → maximal cocktails = 2 → legal.  
• Player 2 adds edge (2, 3) → maximal cocktails = 3 → legal.  
• Player 1 has no edge to add without reducing the count → loses.  

Task  
----
Implement a Python strategy that, given the current `nodes`, `edges`, and the current `cnt_maximal_cocktails`, returns the best edge to add next.

**Input Format:**  
- `nodes`: a list of integers, representing the drug nodes.  
- `edges`: a list of tuples (int, int), each representing an existing harmful interaction.  
- `cnt_maximal_cocktails`: an integer, representing the current number of maximal cocktails.  

**Output Format:**  
- Return a tuple (node1, node2), representing the edge to add next.  

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

class MaxMaximalCocktailsCustomStrategy:  
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
        
        # nodes_list is a list of int  
        nodes_list = data['nodes']  
        # edges_list is a list of tuple, where each tuple is (int, int)  
        edges_list = data['edges']  
        # cnt_maximal_cocktails is a int  
        cnt_maximal_cocktails = data['cnt_maximal_cocktails']  
        
        # return a tuple representing a new edge to add (int, int)  
        new_edge = None  
        # TODO: implement your decision logic here  
        
        return Info(  
            sender=self.__class__.__name__,  
            receiver=message.sender,  
            difficulty=message.difficulty,  
            message=[BaseMessageDataType(data=new_edge, type='custom')]  
        )  

Guidelines  
----------
* The existing template should not be modified. You may **add** functions, data structures, or variables as needed.  
* You can import additional libraries and assume any additional libraries are already installed.  

Required Output Format  
----------------------
Return a single JSON object:

{
  "reasoning": "<your step-by-step explanation>",
  "code": "<only the Python code and the code must be complete that including code in template>"
}

* `reasoning` — concise explanation of how you determined `new_edge`.  
* `code` — complete, syntax-error-free Python implementing the decision logic, with **no** ```python fences or other formatting.'''

PUZZLE_INTRO = '''Game Description
        
Game: Max Maximal Cocktails
        
Overview:
Two players take turns adding edges (representing harmful interactions) to a graph where nodes represent drugs. The goal is to maximize the number of maximal drug combinations, known as maximal cocktails, without reducing their number. The first player to add an edge that reduces the number of maximal cocktails loses the game.

Mechanics:
1. Graph Representation:
- Nodes: Represent drugs.
- Edges: Represent harmful interactions between drugs.
- Maximal Cocktails: These are the maximum independent sets in the graph, representing the largest possible sets of drugs that can be combined without harmful interactions.

2. Objective:
- Players take turns adding an edge to the graph.
- The goal is to increase or maintain the number of maximal cocktails without reducing it.
- The first player to add an edge that decreases the number of maximal cocktails loses.

3. Conditions:
- Each added edge should increase or keep the number of maximal cocktails the same.
- The game ends when a player adds an edge that reduces the number of maximal cocktails.'''