from pydantic import BaseModel
from typing import List, Any

from model.base import BaseStrategy
from system.message import Info
from system.message import BaseMessageDataType
from system.message import StateLegality
from system.message import GameStatus

from puzzle.base import BasePuzzle
from prompts.exclusivity_probes import *

import random


class ExclusivityProbesPuzzle(BasePuzzle):
    dimension: int = 0
    num_particles: int = 0
    distance: int = 0

    particles: List[List[int]] = []
    cnt_guess: List[int] = []
    all_guess: List[List[int]] = []
    true_guess: List[List[int]] = []

    def puzzle_generator(self, models: List[BaseStrategy], difficulty: str, one_shot: bool, tot: bool, iterative: bool, simplified_description: bool, legal_candidates: bool, with_history: bool, code_generation: bool, random_seed: Any, output_dir: str) -> List[Info]:
        self.difficulty = difficulty
        self.code_generation = code_generation
        self.output_dir = output_dir

        if random_seed is not None:
            self.rs = random_seed
            random.seed(random_seed)

        self.cnt_guess = []
        self.all_guess = []
        self.true_guess = []

        if self.difficulty == 'easy':
            self.dimension = random.randint(6, 10)
            self.num_particles = random.randint(2, int(self.dimension / 2))
            self.distance = random.randint(1, int(self.dimension / 2))
        elif self.difficulty == 'normal':
            self.dimension = random.randint(11, 15)
            self.num_particles = random.randint(2, int(self.dimension / 2))
            self.distance = random.randint(1, int(self.dimension / 2))
            
        self.particles = self.generate_vectors(self.num_particles, self.dimension, self.distance)

        init_dict = {'dimension': self.dimension, 'num_particles': self.num_particles, 'distance': self.distance, 'particles': self.particles, 'guess': [], 'is_particle': False}

        self.history['setting'] = {'dimension': self.dimension, 'distance': self.distance, 'num_particles': self.num_particles, 'particles': str(self.particles)}
        self.history['state'] = []

        message_list = []
        model = models[0]
        if self.code_generation:
            message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=CODE_PROMPT, type='text')], generated_type='code'))
        else:
            if model.strategy_type.value != 'LLM':
                message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=init_dict, type='custom')]))
            else:
                nl_description = DESCRIPTION.format(dimension=self.dimension, distance=self.distance, num_particles=self.num_particles)
                message_list.append(Info(sender=self.__class__.__name__, receiver=model.__class__.__name__, difficulty=difficulty, message=[BaseMessageDataType(data=nl_description, type='text')]))
        return message_list
            
    def state_transition_checker(self, message: Info, response: Info, model: BaseStrategy):
        result = response.message[0].data
        if result is None:
            return message, StateLegality.NONE
        else:
            if len(result) != self.dimension:
                return message, StateLegality.TERMINATE
            for value in result:
                if value not in [0, 1]:
                    return message, StateLegality.TERMINATE
            if len(self.all_guess) > 2 ** (self.dimension+1):
                return message, StateLegality.TERMINATE
            return message, StateLegality.LEGAL
        
    def state_transition(self, response: Info, model: BaseStrategy, next_model: Any):
        result = response.message[0].data
        
        self.cnt_guess = result

        is_particle = False
        if result in self.particles:
            is_particle = True
        tmp = {'dimension': self.dimension, 'num_particles': self.num_particles, 'distance': self.distance, 'particles': self.particles, 'guess': result, 'is_particle': is_particle}
        
        self.history['state'].append(f'guess: {result}, is_particle: {is_particle}')   

        if model.strategy_type.value != 'LLM':
            self.all_guess.append(result)
            if result in self.particles and result not in self.true_guess:
                self.true_guess.append(result)
            return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=tmp, type='custom')])
        else:
            nl_description = ''
            if result in self.particles and result not in self.true_guess:
                self.true_guess.append(result)
                nl_description = f'''Your probe on position {result} is a particle. You have found {len(self.true_guess)} particles. Please output the position of your next probe.'''
            elif result in self.particles and result in self.true_guess:
                nl_description = f'''You have already found the particle at position {result}. Please output the position of your next probe.'''
            elif result not in self.particles and result in self.all_guess:
                nl_description = f'''Your probe on position {result} is not a particle. You have probed this position before. Please output the position of your next probe.'''
            else:
                nl_description = f'''Your probe on position {result} is not a particle. You have found {len(self.true_guess)} particles. Please output the position of your next probe.'''
            self.all_guess.append(result)
            return Info(sender=self.__class__.__name__, receiver=next_model.__class__.__name__, difficulty=self.difficulty, message=[BaseMessageDataType(data=nl_description, type='text')])
        
    def game_over_checker(self, model: BaseStrategy):
        if len(self.true_guess) == self.num_particles:
            return GameStatus.END
        else:
            return GameStatus.ONGOING

    def calculate_score(self, game_status: GameStatus, current_player: int):
        if game_status == GameStatus.END:
            self.scores = ['Success - ' + str(len(self.all_guess)) + ' probes']
            return len(self.all_guess)
        else:
            self.scores = ['Invalid' for _ in range(2)]
            return 0
        
    def generate_vectors(self, n, d, k):
        vectors = []

        # Generate the first vector randomly
        first_vector = [random.randint(0, 1) for _ in range(d)]
        vectors.append(first_vector)

        for _ in range(n - 1):
            valid_vector_found = False
            while not valid_vector_found:
                # Start with a copy of one of the existing vectors
                candidate_vector = random.choice(vectors)[:]

                # Flip at least k bits to ensure the distance condition
                flipped_bits = set()
                while len(flipped_bits) < k:
                    bit_index = random.randint(0, d - 1)
                    if bit_index not in flipped_bits:
                        flipped_bits.add(bit_index)
                        candidate_vector[bit_index] = 1 - candidate_vector[bit_index]

                # Check if the candidate vector satisfies the distance condition
                valid = True
                for vector in vectors:
                    hamming_distance = sum(a != b for a, b in zip(candidate_vector, vector))
                    if hamming_distance < k:
                        valid = False
                        break

                if valid:
                    vectors.append(candidate_vector)
                    valid_vector_found = True

        return vectors

    def get_status4simulator(self, player_idx):
        if player_idx >= len(self.scores):
            return None
        return self.scores[player_idx]

    def get_state4simulator(self) -> List[BaseMessageDataType]:
        state = ''
        if len(self.cnt_guess) == 0:
            state += 'Game starts. The dimension is {}, the distance is {}, and the number of particles you need to probe is {}.'.format(self.dimension, self.distance, self.num_particles)
        else:
            if len(self.true_guess) > 0 and self.cnt_guess == self.true_guess[-1]:
                state += f'Your probe on position {self.cnt_guess} is a particle. You have found {len(self.true_guess)} particles.'
            else:
                state += f'Your probe on position {self.cnt_guess} is not a particle. You have found {len(self.true_guess)} particles.'
        return [BaseMessageDataType(data=state, type='text')]

    def get_puzzle_intro4simulator(self) -> List[BaseMessageDataType]:
        puzzle_intro = PUZZLE_INTRO
        return [BaseMessageDataType(data=puzzle_intro, type='text')]

