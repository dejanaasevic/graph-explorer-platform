from typing import Any

class FilterExpression:
    def __init__(self, attribute: str, operator: str, value: Any):
        self.attribute: str = attribute
        self.operator: str = operator
        self.value: Any = value