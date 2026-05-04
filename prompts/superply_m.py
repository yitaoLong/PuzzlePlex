DESCRIPTION = '''You are required to play a game called Superply with another player. This is a path-building board game played on a grid. The objective for Player 1 is to construct a path from the left side of the grid to the right, while Player 2 must build a path from the top to the bottom. A path consists of a sequence of same-color squares such that each square in the path touches the next one on a side or on a corner. The color for Player 1 is red, and the color for Player 2 is blue.

During each turn, a player claims a square by selecting a grid position that satisfies the system-provided hint. If the chosen position is invalid, no changes are made, and the turn passes to the other player.

The hints are mathematical operations, such as "sum is less than 10," meaning that the sum of the numbers in the selected position must be less than 10 (row_indx + column_index < 10). A player may choose any grid position that satisfies the given hint and is unoccupied.

The game board is a grid, and it is 1-indexed, which shows in the image. The first player to successfully build their path wins the game.

For example, if the hint is "product contains digit 6," and the grid converted from the image is as follows:
[[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0]]

Where value 0 means position is unoccupied. If you are Player 1, you can select the position (1, 6), (6, 1), (2, 3), (3, 2) or (6, 6) because the product of the row and column indices is 6, 6, 6, 6 and 36, respectively, and they all contain the digit 6.

If you choose the position (6, 6), the grid becomes:
[[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 0],
[0, 0, 0, 0, 0, 1]]

Please provide your actions in the following format:

Reasoning: Explanation of your choice.
Operation: Specify the position on the grid in the format: `operation = (row_index, column_index)`.\n\n'''  

SIMPLIFIED_DESCRIPTION = None

STATE_TRANSIT_PROMPT = None

PUZZLE_INTRO = '''Game Description
        
Game: Superply
        
Overview:
Superply is a two-player path-building board game played on a 6x6 grid. Player 1’s objective is to construct a path from the left side of the grid to the right, while Player 2 must build a path from the top to the bottom. Each player takes turns claiming grid positions based on system-provided mathematical hints. A valid path consists of adjacent same-value squares, either by a side or corner. Player 1 marks claimed positions with a value of 1, and Player 2 with a value of 2. The first player to complete their path wins.

Mechanics:
1. Grid and Path Construction:
- The grid is initially filled with zeros.
- Player 1 must construct a path from the left side to the right side.
- Player 2 must build a path from the top to the bottom.

2. Hints and Valid Moves:
- On each turn, players receive a mathematical hint, such as "sum is less than 10" or "product contains digit 6."
- Players can select any unclaimed grid position that satisfies the hint to claim.
- If the selected position does not satisfy the hint, the turn is skipped.

3. Objective:
- Each player claims grid positions by following the hints.
- The winner is the first player to successfully build a valid path across the grid.'''