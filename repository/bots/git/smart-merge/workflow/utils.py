import re
from re import Pattern
from typing import AnyStr


def word_pattern(word: str) -> Pattern[AnyStr]:
    return re.compile(r'\b[\w-]*' + re.escape(word) + r'[\w-]*\b', re.IGNORECASE)
