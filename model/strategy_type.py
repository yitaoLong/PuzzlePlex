from enum import Enum

class StrategyType(str, Enum):
    SMT = 'SMT'
    LLM = 'LLM'
    Custom = 'Custom'
    NoneType = 'NoneType'