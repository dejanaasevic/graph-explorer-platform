import datetime
from typing import Any


class FilterExpression:
    """Represent a parsed filter condition made up of an attribute, an operator, and a value.

    Used by QueryEngine.filter to test individual nodes against a condition.
    """

    def __init__(self, attribute: str, operator: str, value: Any):
        """Initialize a FilterExpression.

        Keyword arguments:
        attribute -- the node attribute name to evaluate (stored in lowercase)
        operator  -- the comparison operator as a string (e.g. '==', '>=', '!=')
        value     -- the value to compare against; may be int, float, date, or str
        """
        self.attribute: str = attribute
        self.operator: str = operator
        self.value: Any = value


class Parser:
    """Parse a raw filter expression string into a FilterExpression object."""

    @staticmethod
    def parse(expression: str) -> FilterExpression:
        """Parse a whitespace-separated filter expression string and return a FilterExpression.

        The expression must contain exactly three parts: attribute, operator, and value.
        The value is coerced to the first type that succeeds in this order:
          1. int
          2. float
          3. date  (expected format: DD.MM.YYYY.)
          4. str   (surrounding single or double quotes are stripped)

        Raises ValueError if the expression does not contain exactly three parts.

        Keyword arguments:
        expression -- the raw filter string, e.g. 'age >= 30' or 'birthdate == 01.01.1990.'
        """
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