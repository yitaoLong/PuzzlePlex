from model.base import BaseStrategy
from system.base import BaseSystem
from puzzle.base import BasePuzzle
import argparse
import os
import json
import sys

from system.message import StateLegality
from model.model_base import ModelBase
from init import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Puzzle running')
    # input directory
    parser.add_argument('--input_dir', type=str, help='Input directory', default='result_code')
    # puzzle settings
    parser.add_argument('--puzzle_name', type=str, help='Puzzle name', choices=['TidyTowerPuzzle', 'OptimalTouringPuzzle', 'CountMaximalCocktailsPuzzle', 'RubyRisksPuzzle', 'ExclusivityProbesPuzzle', 'MaxTargetPuzzle', 'CardNimPuzzle', 'SudoKillPuzzle', 'MaxMaximalCocktailsPuzzle', 'ExclusivityParticlesPuzzle', 'BeatOrBombStoPuzzle', 'LargerTargetPuzzle', 'SuperplyPuzzle', 'SudoKillMPuzzle', 'SuperplyMPuzzle'], required=True)
    parser.add_argument('--model_1', type=str, help='Model 1 name', required=True)
    parser.add_argument('--model_2', type=str, help='Model 2 name', default=None)
    parser.add_argument('--num_players', type=int, help='Number of players', default=1)
    parser.add_argument('--difficulty', type=str, help='Difficulty level', choices=['easy', 'normal'], default='easy')
    # seed range
    parser.add_argument('--seed_range', type=str, help='Seed number range', default='1-10')
    # timeout for custom model
    parser.add_argument('--max_time_cost', type=float, help='Max time cost', default=300.0)
    # output directory
    parser.add_argument('--output_dir', type=str, help='Output directory', default='code_competition_results')
    args = parser.parse_args()

    args.output_dir = os.path.abspath(args.output_dir)
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    index = None
    for i in range(len(puzzle_list)):
        if args.puzzle_name == puzzle_list[i].__class__.__name__:
            index = i
            break

    puzzle = puzzle_list[index]

    if '-' not in args.seed_range:
        seeds = [int(args.seed_range)]
    else:
        seeds = list(range(int(args.seed_range.split('-')[0]), int(args.seed_range.split('-')[1]) + 1))

    if args.num_players == 1:
        count = 0
        if args.model_1 == 'custom':
            count = 1
        else:
            count = 32

        data = None
        if args.model_1 != 'custom':
            with open(os.path.join(args.input_dir, args.model_1, str(puzzle.__class__.__name__) + '.json'), 'r') as f:
                data = json.load(f)

        for c in range(count):
            model = None
            if args.model_1 == 'custom':
                model = ModelBase(name='custom')
            else:
                model = ModelBase(name=args.model_1 + '_' + str(c))


            for s in seeds:
                if args.model_1 == 'custom':
                    model_instance = puzzle_custom_list[index](model)
                    system = BaseSystem()
                    score = system.run(web=None, output_dir=args.output_dir, num_players=1, model_name_list=[model_instance], puzzle_name=puzzle, max_time_cost=args.max_time_cost, difficulty=args.difficulty, one_shot=False, tot=False, iterative=False, simplified_description=False, legal_candidates=False, with_history=True, code_generation=False, random_seed=s)
                    model.clear()
                else:
                    code_string = ''
                    for j in range(len(data)):
                        if data[j]['index'] == c:
                            code_string = data[j]['code']
                            break
                    if code_string == '':
                        puzzle.output_dir = args.output_dir
                        puzzle.save_file(0, [puzzle_custom_list[index](model)], StateLegality.NONE, with_history=True)
                        continue

                    # Create a namespace for exec
                    namespace = {}
                    # Execute the code string to define the class
                    try:
                        exec(code_string, namespace)
                    except Exception as e:
                        puzzle.output_dir = args.output_dir
                        puzzle.save_file(0, [puzzle_custom_list[index](model)], StateLegality.SYNTAX_ERROR, with_history=True)
                        continue
                    puzzle_class_name = puzzle_custom_list[index].__name__
                    strategy_class = namespace.get(puzzle_class_name)

                    if strategy_class is None:
                        puzzle.output_dir = args.output_dir
                        puzzle.save_file(0, [puzzle_custom_list[index](model)], StateLegality.NONE, with_history=True)
                        continue

                    try:
                        model_instance = strategy_class(model)
                        system = BaseSystem()
                        score = system.run(web=None, output_dir=args.output_dir, num_players=1, model_name_list=[model_instance], puzzle_name=puzzle, max_time_cost=args.max_time_cost, difficulty=args.difficulty, one_shot=False, tot=False, iterative=False, simplified_description=False, legal_candidates=False, with_history=True, code_generation=False, random_seed=s)
                    except Exception as e:
                        puzzle.output_dir = args.output_dir
                        puzzle.save_file(0, [puzzle_custom_list[index](model)], StateLegality.RUNTIME_ERROR, with_history=True)
                        continue
                    model.clear()
    else:
        data1 = None
        data2 = None
        if args.model_1 != 'custom':
            with open(os.path.join(args.input_dir, args.model_1, str(puzzle.__class__.__name__) + '.json'), 'r') as f:
                data1 = json.load(f)
        if args.model_2 != 'custom':
            with open(os.path.join(args.input_dir, args.model_2, str(puzzle.__class__.__name__) + '.json'), 'r') as f:
                data2 = json.load(f)

        if args.model_1 == 'custom' or args.model_2 == 'custom':
            for c in range(32):
                if args.model_1 == 'custom':
                    model1 = ModelBase(name='custom')
                    model2 = ModelBase(name=args.model_2 + '_' + str(c))
                else:
                    model1 = ModelBase(name=args.model_1 + '_' + str(c))
                    model2 = ModelBase(name='custom')
                for s in seeds:
                    if args.model_1 == 'custom':
                        model_instance1 = puzzle_custom_list[index](model1)

                        code_string = ''
                        for j in range(len(data2)):
                            if data2[j]['index'] == c:
                                code_string = data2[j]['code']
                                break
                        if code_string == '':
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(0, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.NONE, with_history=True)
                            continue
                        # Create a namespace for exec
                        namespace = {}
                        # Execute the code string to define the class
                        try:
                            exec(code_string, namespace)
                        except Exception as e:
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(0, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.SYNTAX_ERROR, with_history=True)
                            continue
                        puzzle_class_name = puzzle_custom_list[index].__name__
                        strategy_class = namespace.get(puzzle_class_name)
                        if strategy_class is None:
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(0, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.NONE, with_history=True)
                            continue
                        try:
                            model_instance2 = strategy_class(model2)
                        except Exception as e:
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(0, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.RUNTIME_ERROR, with_history=True)
                            continue
                        try:
                            system = BaseSystem()
                            score = system.run(web=None, output_dir=args.output_dir, num_players=2, model_name_list=[model_instance1, model_instance2], puzzle_name=puzzle, max_time_cost=args.max_time_cost, difficulty=args.difficulty, one_shot=False, tot=False, iterative=False, simplified_description=False, legal_candidates=False, with_history=True, code_generation=False, random_seed=s)
                            model1.clear()
                            model2.clear()
                        except Exception as e:
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(1-system.current_player, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.RUNTIME_ERROR, with_history=True)
                            continue
                    else:
                        model_instance2 = puzzle_custom_list[index](model2)
                        code_string = ''
                        for j in range(len(data1)):
                            if data1[j]['index'] == c:
                                code_string = data1[j]['code']
                                break
                        if code_string == '':
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(1, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.NONE, with_history=True)
                            continue
                        # Create a namespace for exec
                        namespace = {}
                        # Execute the code string to define the class
                        try:
                            exec(code_string, namespace)
                        except Exception as e:
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(1, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.SYNTAX_ERROR, with_history=True)
                            continue
                        puzzle_class_name = puzzle_custom_list[index].__name__
                        strategy_class = namespace.get(puzzle_class_name)
                        if strategy_class is None:
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(1, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.NONE, with_history=True)
                            continue
                        try:
                            model_instance1 = strategy_class(model1)
                        except Exception as e:
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(1, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.RUNTIME_ERROR, with_history=True)
                            continue
                        try:
                            system = BaseSystem()
                            score = system.run(web=None, output_dir=args.output_dir, num_players=2, model_name_list=[model_instance1, model_instance2], puzzle_name=puzzle, max_time_cost=args.max_time_cost, difficulty=args.difficulty, one_shot=False, tot=False, iterative=False, simplified_description=False, legal_candidates=False, with_history=True, code_generation=False, random_seed=s)
                            model1.clear()
                            model2.clear()
                        except Exception as e:
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(1-system.current_player, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.RUNTIME_ERROR, with_history=True)
                            continue
        else:
            for c1 in range(32):
                model1 = ModelBase(name=args.model_1 + '_' + str(c1))
                for c2 in range(32):
                    model2 = ModelBase(name=args.model_2 + '_' + str(c2))
                    for s in seeds:
                        code_string1 = ''
                        for j in range(len(data1)):
                            if data1[j]['index'] == c1:
                                code_string1 = data1[j]['code']
                                break
                        if code_string1 == '':
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(1, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.NONE, with_history=True)
                            continue
                        # Create a namespace for exec
                        namespace1 = {}
                        # Execute the code string to define the class
                        try:
                            exec(code_string1, namespace1)
                        except Exception as e:
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(1, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.SYNTAX_ERROR, with_history=True)
                            continue
                        puzzle_class_name1 = puzzle_custom_list[index].__name__
                        strategy_class1 = namespace1.get(puzzle_class_name1)
                        if strategy_class1 is None:
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(1, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.NONE, with_history=True)
                            continue
                        try:
                            model_instance1 = strategy_class1(model1)
                        except Exception as e:
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(1, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.RUNTIME_ERROR, with_history=True)
                            continue
                        code_string2 = ''
                        for j in range(len(data2)):
                            if data2[j]['index'] == c2:
                                code_string2 = data2[j]['code']
                                break
                        if code_string2 == '':
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(0, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.NONE, with_history=True)
                            continue
                        # Create a namespace for exec
                        namespace2 = {}
                        # Execute the code string to define the class
                        try:
                            exec(code_string2, namespace2)
                        except Exception as e:
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(0, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.SYNTAX_ERROR, with_history=True)
                            continue
                        puzzle_class_name2 = puzzle_custom_list[index].__name__
                        strategy_class2 = namespace2.get(puzzle_class_name2)
                        if strategy_class2 is None:
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(0, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.NONE, with_history=True)
                            continue
                        try:
                            model_instance2 = strategy_class2(model2)
                        except Exception as e:
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(0, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.RUNTIME_ERROR, with_history=True)
                            continue
                        try:
                            system = BaseSystem()
                            score = system.run(web=None, output_dir=args.output_dir, num_players=2, model_name_list=[model_instance1, model_instance2], puzzle_name=puzzle, max_time_cost=args.max_time_cost, difficulty=args.difficulty, one_shot=False, tot=False, iterative=False, simplified_description=False, legal_candidates=False, with_history=True, code_generation=False, random_seed=s)
                            model1.clear()
                            model2.clear()
                        except Exception as e:
                            puzzle.output_dir = args.output_dir
                            puzzle.save_file(1-system.current_player, [puzzle_custom_list[index](model1), puzzle_custom_list[index](model2)], StateLegality.RUNTIME_ERROR, with_history=True)
                            continue