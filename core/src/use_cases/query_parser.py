import datetime
from typing import Any

class FilterExpression:
    def __init__(self, attribute: str, operator: str, value: Any):
        self.attribute: str = attribute
        self.operator: str = operator
        self.value: Any = value

class Parser:
    @staticmethod
    def parse(expression: str) -> FilterExpression:
        parts = expression.strip().split(maxsplit=2)
        if len(parts) != 3:
            raise ValueError(f"Invalid filter expression: '{expression}'")

        attribute, operator, value = parts

        try:
            value_parsed: Any = int(value)
        except ValueError:
            try:
                value_parsed = float(value)
            except ValueError:
                try:
                    value_parsed = datetime.datetime.strptime(value, "%d.%m.%Y.").date()
                except ValueError:
                    value_parsed = value.strip('"').strip("'")

        return FilterExpression(attribute.lower(), operator, value_parsed)