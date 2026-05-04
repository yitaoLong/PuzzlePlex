from model.base import BaseStrategy
from system.base import BaseSystem
from puzzle.base import BasePuzzle
import argparse
import os

from model.model_base import ModelBase
from init import *

import torch

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Puzzle Running')

    # puzzle settings
    parser.add_argument('--puzzle_name', type=str, help='Puzzle name', choices=['TidyTowerPuzzle', 'OptimalTouringPuzzle', 'CountMaximalCocktailsPuzzle', 'RubyRisksPuzzle', 'ExclusivityProbesPuzzle', 'MaxTargetPuzzle', 'CardNimPuzzle', 'SudoKillPuzzle', 'MaxMaximalCocktailsPuzzle', 'ExclusivityParticlesPuzzle', 'BeatOrBombStoPuzzle', 'LargerTargetPuzzle', 'SuperplyPuzzle', 'SudoKillMPuzzle', 'SuperplyMPuzzle'], required=True)
    parser.add_argument('--model_1', type=str, help='Model 1 name', required=True)
    parser.add_argument('--model_2', type=str, help='Model 2 name', default=None)
    parser.add_argument('--num_players', type=int, help='Number of players', default=1)
    parser.add_argument('--difficulty', type=str, help='Difficulty level', choices=['easy', 'normal'], default='easy')
    # seed range
    parser.add_argument('--seed_range', type=str, help='Seed number range', default='1-10')
    # one-shot prompting
    parser.add_argument('--one_shot', type=bool, help='One-shot prompting', default=False)
    # ToT prompting
    parser.add_argument('--tot', type=bool, help='ToT prompting', default=False)
    # description of the puzzle
    parser.add_argument('--simplified_description', type=bool, help='Simplified description of the puzzle', default=False)
    # iterative or single-pass in single deterministic puzzles
    parser.add_argument('--iterative', type=bool, help='Iterative or single-pass in single deterministic puzzles', default=False)
    # legal candidates
    parser.add_argument('--legal_candidates', type=bool, help='Legal candidates', default=False)
    # with history
    parser.add_argument('--with_history', type=bool, help='With history', default=True)
    # code generation
    parser.add_argument('--code_generation', type=bool, help='Code generation', default=False)

    # timeout for custom model
    parser.add_argument('--max_time_cost', type=float, help='Max time cost', default=300.0)

    # inference settings
    parser.add_argument('--max_new_tokens', type=int, help='Max new tokens', default=8192)

    # output directory
    parser.add_argument('--output_dir', type=str, help='Output directory', default='instruction_based_results')

    # web UI
    parser.add_argument("--web", action="store_true", help="Use web UI for output")

    args = parser.parse_args()

    args.output_dir = os.path.abspath(args.output_dir)
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    

    model1 = ModelBase(name=args.model_1, max_new_tokens=args.max_new_tokens)
    model1.load_model()

    index = None
    for i in range(len(puzzle_list)):
        if args.puzzle_name == puzzle_list[i].__class__.__name__:
            index = i
            break

    puzzle = puzzle_list[index]

    if not os.path.exists(args.output_dir + '/' + args.model_1):
        os.makedirs(args.output_dir + '/' + args.model_1)

    # sample 32 times
    for time in range(32):
        print('Sample:', time)
        model_instance1 = puzzle_llm_list[index](model1)
        system = BaseSystem()
        score = system.run(web=args.web, output_dir = args.output_dir + '/' + args.model_1, num_players=1, model_name_list=[model_instance1], puzzle_name=puzzle, max_time_cost=args.max_time_cost, difficulty='easy', one_shot=False, tot=False, iterative=False, simplified_description=False, legal_candidates=False, with_history=True, code_generation=True, random_seed=1)
        model1.clear()