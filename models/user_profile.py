from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

@dataclass
class UserProfile:
    target_score: float
    exam_date: str
    daily_minutes: int
    weakest_skill: str
    momentum_score: int = 0
    last_check_in: str = field(default_factory=lambda: str(date.today()))
    current_streak: int = 0
    max_streak: int = 0
    skips_left: int = 1
    last_skip_grant: str = field(default_factory=lambda: str(date.today()))
    badges: list = field(default_factory=list)

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        valid_keys = cls.__annotations__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)