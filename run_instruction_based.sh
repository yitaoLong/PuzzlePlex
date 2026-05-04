#!/bin/bash

model_list=('custom' 'gpt-4.1' 'o4-mini' 'gemini-2.5-pro-preview-03-25' 'grok-3-mini-beta' 'deepseek-reasoner' 'deepseek-chat' 'phi-4-multimodal-instruct' 'qwq' 'llama' 'gemma' 'qwen')
difficulty_levels=('easy' 'normal')


# single player deterministic puzzles
single_player_deterministic_puzzles=('TidyTowerPuzzle' 'OptimalTouringPuzzle' 'CountMaximalCocktailsPuzzle')
for model in "${model_list[@]}"; do
    for puzzle in "${single_player_deterministic_puzzles[@]}"; do
        for difficulty in "${difficulty_levels[@]}"; do
            python3 run_instruction_based.py \
                --puzzle_name "$puzzle" \
                --model_1 "$model" \
                --num_players 1 \
                --difficulty "$difficulty" \
                --seed_range '1-10' \
                --output_dir 'instruction_based_results'
        done
    done
done


# two player deterministic puzzles
two_player_deterministic_puzzles=('CardNimPuzzle' 'SudoKillPuzzle' 'MaxMaximalCocktailsPuzzle' 'ExclusivityParticlesPuzzle' 'SuperplyPuzzle')
for ((idx1=0; idx1<${#model_list[@]}; idx1++)); do
    for ((idx2=idx1+1; idx2<${#model_list[@]}; idx2++)); do
        model_1=${model_list[idx1]}
        model_2=${model_list[idx2]}
        for puzzle in "${two_player_deterministic_puzzles[@]}"; do
            for difficulty in "${difficulty_levels[@]}"; do
                python3 run_instruction_based.py \
                    --puzzle_name "$puzzle" \
                    --model_1 "$model_1" \
                    --model_2 "$model_2" \
                    --num_players 2 \
                    --difficulty "$difficulty" \
                    --seed_range '1-5' \
                    --output_dir 'instruction_based_results'
                # swap models
                python3 run_instruction_based.py \
                    --puzzle_name "$puzzle" \
                    --model_1 "$model_2" \
                    --model_2 "$model_1" \
                    --num_players 2 \
                    --difficulty "$difficulty" \
                    --seed_range '1-5' \
                    --output_dir 'instruction_based_results'
            done
        done
    done
done


# two player deterministic text-image puzzles
two_player_deterministic_image_puzzles=('SudoKillMPuzzle' 'SuperplyMPuzzle')
model_list=('custom' 'gpt-4.1' 'o4-mini' 'gemini-2.5-pro-preview-03-25' 'phi-4-multimodal-instruct' 'gemma' 'qwen')
for ((idx1=0; idx1<${#model_list[@]}; idx1++)); do
    for ((idx2=idx1+1; idx2<${#model_list[@]}; idx2++)); do
        model_1=${model_list[idx1]}
        model_2=${model_list[idx2]}
        for puzzle in "${two_player_deterministic_image_puzzles[@]}"; do
            for difficulty in "${difficulty_levels[@]}"; do
                python3 run_instruction_based.py \
                    --puzzle_name "$puzzle" \
                    --model_1 "$model_1" \
                    --model_2 "$model_2" \
                    --num_players 2 \
                    --difficulty "$difficulty" \
                    --seed_range '1-5' \
                    --output_dir 'instruction_based_results'
                # swap models
                python3 run_instruction_based.py \
                    --puzzle_name "$puzzle" \
                    --model_1 "$model_2" \
                    --model_2 "$model_1" \
                    --num_players 2 \
                    --difficulty "$difficulty" \
                    --seed_range '1-5' \
                    --output_dir 'instruction_based_results'
            done
        done
    done
done
