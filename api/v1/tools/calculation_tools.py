from typing import List, Dict, Union, Any
from langchain.tools import Tool
from langchain.chains import LLMMathChain
from langchain_community.utilities.wolfram_alpha import WolframAlphaAPIWrapper


class FinancialCalculationTools:
    def __init__(self, llm):
        self.llm = llm
        self.execution_cache = {}

        # Initialize core financial tools
        self.financial_tools = [
            self.create_tool(
                self.calculate_total,
                "Sum numerical values (handles int/float/string inputs)"
            ),
            self.create_tool(
                self.calculate_average,
                "Compute average of numerical values"
            ),
            self.create_tool(
                self.calculate_percentage,
                "Calculate percentage (part/whole)*100"
            ),
            self.create_tool(
                self.extract_values_by_year,
                "Extract and aggregate financial data by year"
            )
        ]

        # Initialize advanced math tools
        self.math_tools = [
            self.create_math_tool(),
            self.create_dupont_tool(),
            self.create_ratio_tool()
        ]

        # Combine all tools
        self.tools = self.financial_tools + self.math_tools

    def create_tool(self, func, description):
        """Create LangChain tool from function"""
        return Tool.from_function(
            func=func,
            name=func.__name__,
            description=description,
            handle_tool_error=True
        )

    def create_math_tool(self):
        """Create LLMMathChain-based calculator"""
        math_chain = LLMMathChain.from_llm(llm=self.llm)
        return Tool(
            name="Advanced_Calculator",
            description="Solves complex math expressions and equations",
            func=math_chain.run,
            handle_tool_error=True
        )

    def create_dupont_tool(self):
        return Tool.from_function(
            func=self.calculate_dupont_roe,
            name="calculate_dupont_roe",
            description="Calculate ROE using DuPont formula: (NetProfitMargin% × AssetTurnover × Leverage)",
            handle_tool_error=True
        )

    def create_ratio_tool(self):
        return Tool.from_function(
            func=self.calculate_ratio,
            name="calculate_ratio",
            description="Calculate financial ratios (numerator/denominator)",
            handle_tool_error=True
        )

    def execute_tool(self, tool_name, *args):
        """Execute a tool with caching to prevent redundant executions."""
        cache_key = (tool_name, args)
        if cache_key in self.execution_cache:
            return self.execution_cache[cache_key]

        # Find the tool by name
        tool = next((t for t in self.tools if t.name == tool_name), None)
        if tool:
            result = tool.func(*args)
            self.execution_cache[cache_key] = result
            return result
        else:
            return f"Tool {tool_name} not found."

    # Core calculation methods
    def calculate_total(self, values: List[Union[int, float, str]]) -> str:
        """Sum values with type conversion"""
        return self.execute_tool("calculate_total", values)

    def calculate_average(self, values: List[Union[int, float, str]]) -> str:
        """Calculate average with empty list handling"""
        return self.execute_tool("calculate_average", values)

    def calculate_percentage(self, part: float, whole: float) -> str:
        """Percentage calculation with zero division guard"""
        return self.execute_tool("calculate_percentage", part, whole)

    def extract_values_by_year(self, data: List[Dict], year_key: str, value_key: str) -> Dict:
        """Year-based financial data aggregation"""
        return self.execute_tool("extract_values_by_year", data, year_key, value_key)

    def calculate_dupont_roe(self, npm: float, at: float, fl: float) -> str:
        """Calculate Return on Equity using DuPont formula"""
        return self.execute_tool("calculate_dupont_roe", npm, at, fl)

    def calculate_ratio(self, numerator: float, denominator: float) -> str:
        """Calculate financial ratio"""
        return self.execute_tool("calculate_ratio", numerator, denominator)

    def get_tools_metadata(self) -> tuple:
        """Return formatted tools list and names"""
        descriptions = [f"{t.name}: {t.description}" for t in self.tools]
        names = [t.name for t in self.tools]
        return "\n".join(descriptions), ", ".join(names)
