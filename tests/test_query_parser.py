import datetime
import  pytest
from use_cases.query_parser import Parser, FilterExpression

class TestFilterExpression:
    def test_stores_values(self):
        expression = FilterExpression("age", ">=", 30)
        assert expression.attribute == "age"
        assert expression.operator == ">="
        assert expression.value == 30

class TestParser:
    def test_parses_int(self):
        expression = Parser.parse("age >= 30")
        assert expression.value == 30
        assert isinstance(expression.value, int)

    def test_parses_float(self):
        expression = Parser.parse("score > 4.5")
        assert expression.value == pytest.approx(4.5)
        assert isinstance(expression.value, float)

    def test_parses_date(self):
        expression = Parser.parse("birthdate == 24.09.2004.")
        assert expression.value == datetime.date(2004, 9, 24)

    def test_parses_string_double_quotes(self):
        expression = Parser.parse('city == "Novi Sad"')
        assert expression.value == "Novi Sad"

    def test_parses_string_single_quotes(self):
        expression = Parser.parse("city == 'Novi Sad'")
        assert expression.value == "Novi Sad"

    def test_parses_bare_string(self):
        expression = Parser.parse("status == active")
        assert expression.value == "active"

    def test_attribute_lowercased(self):
        expression = Parser.parse("Age == 24")
        assert expression.attribute == "age"

    def test_operator_preserved(self):
        for operation in ("==", "!=", ">", ">=", "<", "<="):
            expression = Parser.parse(f"x {operation} 1")
            assert expression.operator == operation

    def test_extra_leading_trailing_whitespace(self):
        expression = Parser.parse("  age == 10  ")
        assert expression.attribute == "age"
        assert expression.value == 10

    def test_raises_on_too_few_parts(self):
        with pytest.raises(ValueError):
            Parser.parse("age ==")

    def test_raises_on_empty_string(self):
        with pytest.raises(ValueError):
            Parser.parse("")

    def test_raises_on_only_attribute(self):
        with pytest.raises(ValueError):
            Parser.parse("age")
