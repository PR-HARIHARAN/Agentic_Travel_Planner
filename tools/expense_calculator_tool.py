from utils.expense_calculator import Calculator
from typing import List, Union
from langchain.tools import tool

class CalculatorTool:
    def __init__(self):
        self.calculator = Calculator()
        self.calculator_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """Setup all tools for the calculator tool"""
        @tool
        def estimate_total_hotel_cost(price_per_night: float, total_days: float) -> float:
            """Calculate total hotel cost"""
            return self.calculator.multiply(price_per_night, total_days)
        
        @tool
        def calculate_total_expense(costs: Union[List[float], float, str]) -> float:
            """Calculate total expense of the trip.

            Accepts either a list of costs, a single numeric cost, or a comma-separated
            string of costs.
            """
            if isinstance(costs, (int, float)):
                return self.calculator.calculate_total(float(costs))

            if isinstance(costs, str):
                values = [float(item.strip()) for item in costs.split(",") if item.strip()]
                return self.calculator.calculate_total(*values)

            return self.calculator.calculate_total(*[float(value) for value in costs])
        
        @tool
        def calculate_daily_expense_budget(total_cost: float, days: int) -> float:
            """Calculate daily expense"""
            return self.calculator.calculate_daily_budget(total_cost, days)
        
        return [estimate_total_hotel_cost, calculate_total_expense, calculate_daily_expense_budget]