from dataclasses import dataclass, asdict
from typing import Dict, Any
import json


@dataclass
class Task:
    
    type: str
    payload: Dict[str, Any]
    retries: int = 3

    def to_json(self) -> str:
        
        return json.dumps(asdict(self))
    
    @staticmethod
    def from_json(json_str: str) -> 'Task':
        
        data = json.loads(json_str)
        return Task(
            type=data['type'],
            payload=data['payload'],
            retries=data.get('retries', 3)
        )


@dataclass
class Metrics:
    total_jobs_in_queue: int = 0
    jobs_done: int = 0
    jobs_failed: int = 0
    
    def to_dict(self) -> Dict[str, int]:
        return asdict(self)