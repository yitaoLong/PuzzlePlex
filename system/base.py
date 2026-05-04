from pydantic import BaseModel
from typing import List, Optional, Any
import signal
import time

from model.base import BaseStrategy
from puzzle.base import BasePuzzle
from system.message import Info
from system.message import StateLegality
from system.message import GameStatus

from system.simulator.app import send_ui_message, stop_web_ui, send_stats, run_web_ui, stop_event
import base64
from io import BytesIO


class BaseSystem(BaseModel):
    models: List[Any] = []
    models_time_cost: List[float] = []
    puzzle: BasePuzzle = None
    puzzle_init_message_list: List[Info] = None
    current_message: Info = None
    current_response: Info = None
    current_state_legality: StateLegality = None
    current_game_status: GameStatus = GameStatus.ONGOING

    web: Any = None
    output_dir: str = ''
    num_players: int = 1
    max_time_cost: float = 300.0
    current_player: int = 0
    difficulty: str = ''
    iterative: bool = False
    random_seed: Any = None
    simplified_description: bool = False
    one_shot: bool = False
    tot: bool = False
    legal_candidates: bool = False
    with_history: bool = True
    code_generation: bool = False

    # Register model
    def model_registry(self, model: Any):
        self.models.append(model)
        self.models_time_cost.append(0.0)

    # Register puzzle
    def puzzle_registry(self, puzzle: BasePuzzle):
        self.puzzle = puzzle
    
    # Instantiate puzzle
    def instantiate_puzzle(self):
        # Get initial message list for the puzzle
        self.puzzle_init_message_list = self.puzzle.puzzle_generator(self.models, self.difficulty, self.one_shot, self.tot, self.iterative, self.simplified_description, self.legal_candidates, self.with_history, self.code_generation, self.random_seed, self.output_dir)
        
        # initialize the simulator if web is enabled
        if self.web:
            self.init_simulator()

        for message in self.puzzle_init_message_list:
            if message.receiver == self.models[self.current_player].__class__.__name__:

                self.current_message = message
                break
    
    # Send message to model
    def send_message(self):
        # send to model input if web is enabled
        if self.web:
            components = self.simulator_components(self.current_message.message)
            self.game_send_message(self.models[self.current_player].name, {'role': self.models[self.current_player].name, 'components': components})

        if self.models[self.current_player].strategy_type.value == 'LLM':
            self.current_response = self.models[self.current_player].receive_message(self.current_message)
            # send to model output if web is enabled
            if self.web:
                # get raw output
                components = []
                components.append({'type': 'text', 'content': '<p style="color:red;">Raw Output:</p>'})
                if self.models[self.current_player].get_raw_output4simulator() is not None:
                    components.extend(self.simulator_components(self.models[self.current_player].get_raw_output4simulator()))
                    self.game_send_message(self.models[self.current_player].name, {'role': self.models[self.current_player].name, 'components': components})
                # get refined output
                components = []
                components.append({'type': 'text', 'content': '<p style="color:red;">Refined Output:</p>'})
                components.extend(self.simulator_components(self.current_response.message))
                self.game_send_message(self.models[self.current_player].name, {'role': self.models[self.current_player].name, 'components': components})
                # get status
                cnt_status = self.puzzle.get_status4simulator(self.current_player)
                if cnt_status is not None:
                    self.game_send_stats(self.models[self.current_player].name, cnt_status)
        else:
            # for custom model, set timeout
            class TimeoutException(Exception):
                pass
            def signal_handler(sig, frame):
                raise TimeoutException('Timeout')
            signal.signal(signal.SIGALRM, signal_handler)

            signal.alarm(round(self.max_time_cost-self.models_time_cost[self.current_player]))
            start_time = time.time()
            try:

                self.current_response = self.models[self.current_player].receive_message(self.current_message)
                # send to model output if web is enabled
                if self.web:
                    components = self.simulator_components(self.current_response.message)
                    self.game_send_message(self.models[self.current_player].name, {'role': self.models[self.current_player].name, 'components': components})
                    # get status
                    cnt_status = self.puzzle.get_status4simulator(self.current_player)
                    if cnt_status is not None:
                        self.game_send_stats(self.models[self.current_player].name, cnt_status)
                signal.alarm(0)
            except TimeoutException as e:
                print('e:', e)
                return TimeoutError
            except Exception as e:
                return False
            finally:
                signal.alarm(0)
                end_time = time.time()
                self.models_time_cost[self.current_player] += end_time - start_time
        return None

    # Check state transition legality
    def state_transition_legality(self):
        self.current_message, self.current_state_legality = self.puzzle.state_transition_checker(self.current_message, self.current_response, self.models[self.current_player])
        return self.current_state_legality
    
    # Check if game is over
    def is_game_over(self):
        if self.num_players == 2:
            updated_message = self.puzzle.state_transition(self.current_response, self.models[self.current_player], self.models[1 - self.current_player])
        else:
            updated_message = self.puzzle.state_transition(self.current_response, self.models[self.current_player], None)

        # update the state if web is enabled
        if self.web:
            components = self.simulator_components(self.puzzle.get_state4simulator())
            self.game_send_message('system', {'role': self.models[self.current_player].name, 'components': components})

        if self.num_players == 2:
            next_player = 1 - self.current_player
        else:
            next_player = self.current_player
        self.current_message = updated_message
        self.current_game_status = self.puzzle.game_over_checker(self.models[next_player])
        return self.current_game_status
    
    # End the game and calculate score, save file
    def end(self):
        if self.code_generation:
            score = None
            self.puzzle.save_code(self.current_response, self.models)
        else:
            score =  self.puzzle.calculate_score(self.current_game_status, self.current_player)
            self.puzzle.save_file(score, self.models, self.current_state_legality, self.with_history)

        # stop the simulator if web is enabled
        if self.web:
            # update status
            for idx in range(len(self.models)):
                cnt_status = self.puzzle.get_status4simulator(idx)
                if cnt_status is not None:
                    self.game_send_stats(self.models[idx].name, cnt_status)

            # Ensure simulator is stopped
            self.stop_simulator()
            
            # Wait for the stop event to be set
            start_time = time.time()
            while not stop_event.is_set() and time.time() - start_time < 5:
                time.sleep(0.1)

        return score
    
    # Run the game
    def run(self, web: Any, output_dir: str, num_players: int, model_name_list: List[Any], puzzle_name: BasePuzzle, max_time_cost: float = 300.0, difficulty: str = 'easy', one_shot: bool = False, tot: bool = False, iterative: bool = False, simplified_description: bool = False, legal_candidates: bool = False, with_history: bool = True, code_generation: bool = False, random_seed: Any = None):
        self.web = web
        self.output_dir = output_dir
        self.num_players = num_players
        self.max_time_cost = max_time_cost
        self.difficulty = difficulty
        self.random_seed = random_seed
        self.simplified_description = simplified_description
        self.iterative = iterative
        self.one_shot = one_shot
        self.tot = tot
        self.legal_candidates = legal_candidates
        self.with_history = with_history
        self.code_generation = code_generation

        for model_name in model_name_list:
            self.model_registry(model_name)

        self.puzzle_registry(puzzle_name)
        self.instantiate_puzzle()

        if self.code_generation:
            self.send_message()
        else:
            while True:
                return_value = self.send_message()
                if return_value == TimeoutError:
                    self.current_state_legality = StateLegality.TIMEOUT
                    break
                elif return_value == False:
                    self.current_state_legality = StateLegality.RUNTIME_ERROR
                    break
                else:
                    self.state_transition_legality()
                    if self.current_state_legality == StateLegality.TERMINATE or self.current_state_legality == StateLegality.NONE:
                        break
                    elif self.current_state_legality == StateLegality.LEGAL:
                        status = self.is_game_over()
                        if status == GameStatus.END:
                            break
                        elif status == GameStatus.ONGOING:
                            if self.num_players == 2:
                                self.current_player = 1 - self.current_player
                            continue
            
        return self.end()
    
    def init_simulator(self):
        c = []
        g = []
        roles_count = 0
        
        c.append({'type': 'system', 'id': roles_count, 'messages': [{'role': 'system', 'components': self.simulator_components(self.puzzle.get_puzzle_intro4simulator())}, {'role': 'system', 'components': self.simulator_components(self.puzzle.get_state4simulator())}]})
        roles_count += 1
        
        for model in self.models:
            c.append({'type': model.name, 'id': roles_count, 'messages': []})
            g.append({'type': model.name, 'value': ''})
            roles_count += 1

        run_web_ui(c, g, self.puzzle.__class__.__name__.replace('Puzzle', ''))
        
    def stop_simulator(self):
        stop_web_ui()

    def game_send_message(self, role, data):
        send_ui_message(role, data)

    def game_send_stats(self, role, value):
        send_stats(role, value)

    def simulator_components(self, message_list):
        components = []
        for m in message_list:
            if m.type == 'image':
                buffered = BytesIO()
                m.data.save(buffered, format="JPEG") 
                components.append({'type': 'image', 'content': base64.b64encode(buffered.getvalue()).decode()})
            else:
                components.append({'type': 'text', 'content': str(m.data).replace('\n', '<br>')})
        return components