from pydantic import BaseModel, PrivateAttr
from typing import List, Optional, Dict, Any, ClassVar
from abc import ABC, abstractmethod

from system.message import Info
from system.message import BaseMessageDataType


class BaseStrategy(BaseModel, ABC):
    _id: int = PrivateAttr()
    _counter: ClassVar[int] = 0

    def __init__(self, **data):
        super().__init__(**data)
        self._id = BaseStrategy._counter
        BaseStrategy._counter += 1

    @property
    def id(self) -> int:
        return self._id

    @abstractmethod
    def load_model(self):
        pass
        
    @abstractmethod
    def generate(self, message_data: Any):
        pass
    
    @abstractmethod
    def get_raw_output4simulator(self) -> List[BaseMessageDataType]:
        pass
    
    @abstractmethod
    def receive_message(self, message: Info) -> Info:
        pass