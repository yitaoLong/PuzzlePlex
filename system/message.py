from pydantic import BaseModel
from typing import List, Optional, Any
from enum import Enum


class BaseMessageDataType(BaseModel):
    data: Any = None
    type: Any = None


class Info(BaseModel):
    sender: str
    receiver: str
    difficulty: str = None
    message: List[BaseMessageDataType] = None
    generated_type: str = 'text'
    with_history: bool = True


class StateLegality(str, Enum):
    LEGAL = 'LEGAL'
    TERMINATE = 'TERMINATE'
    NONE = 'NONE'
    TIMEOUT = 'TIMEOUT'
    RUNTIME_ERROR = 'RUNTIME_ERROR'
    SYNTAX_ERROR = 'SYNTAX_ERROR'


class GameStatus(str, Enum):
    ONGOING = 'ONGOING'
    END = 'END'