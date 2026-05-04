#!/bin/bash

model_list=('gpt-4.1' 'o4-mini' 'gemini-2.5-pro-preview-03-25' 'grok-3-mini-beta' 'deepseek-reasoner' 'deepseek-chat' 'phi-4-multimodal-instruct' 'qwq' 'llama' 'gemma' 'qwen')
puzzles=('TidyTowerPuzzle' 'OptimalTouringPuzzle' 'CountMaximalCocktailsPuzzle' 'RubyRisksPuzzle' 'ExclusivityProbesPuzzle' 'MaxTargetPuzzle' 'CardNimPuzzle' 'SudoKillPuzzle' 'MaxMaximalCocktailsPuzzle' 'ExclusivityParticlesPuzzle' 'SuperplyPuzzle' 'BeatOrBombStoPuzzle' 'LargerTargetPuzzle')

# code generation
for model in "${model_list[@]}"; do
    for puzzle in "${puzzles[@]}"; do
        python3 run_code_based.py \
            --puzzle_name "$puzzle" \
            --model_1 "$model" \
            --code_generation True \
            --output_dir 'result_code'
    done
done


