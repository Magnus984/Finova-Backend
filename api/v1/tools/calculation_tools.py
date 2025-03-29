from langchain.tools import Tool
from langchain.chains import LLMMathChain
from typing import List, Dict, Union, Any
import json
import logging


class FinancialCalculationTools:
    def __init__(self, llm):
        self.llm = llm
        self.execution_cache = {}
        self.tools = self._initialize_tools()

    def _initialize_tools(self):
        return [
            self._create_tool(self.calculate_total),
            self._create_tool(self.calculate_average),
            self._create_tool(self.calculate_percentage),
            self._create_math_tool(),
            self._create_tool(self.extract_values_by_year),
            self._create_dupont_tool(),
            self._create_ratio_tool()
        ]

    def _create_tool(self, func):
        return Tool.from_function(
            func=func,
            name=func.__name__,
            description=func.__doc__,
            handle_tool_error=True
        )

    def _create_math_tool(self):
        math_chain = LLMMathChain.from_llm(llm=self.llm)
        return Tool(
            name="Advanced_Calculator",
            description="Solves complex math expressions and equations. Use for complex calculations beyond simple arithmetic. Input: a math expression as a string. Output: the calculated result.",
            func=math_chain.run,
            handle_tool_error=True
        )

    def _create_dupont_tool(self):
        return Tool.from_function(
            func=self.calculate_dupont_roe,
            name="calculate_dupont_roe",
            description="Calculate ROE using the DuPont formula: (NetProfitMargin% × AssetTurnover × Leverage). Input: three float values representing npm (net profit margin percentage), at (asset turnover), and fl (financial leverage). Output: ROE as a percentage (float).",
            handle_tool_error=True
        )

    def _create_ratio_tool(self):
        return Tool.from_function(
            func=self.calculate_ratio,
            name="calculate_ratio",
            description="Calculate financial ratios by dividing numerator by denominator. Use for any financial ratio calculation. Input: two float values (numerator and denominator). Output: the ratio as a float value with 4 decimal precision.",
            handle_tool_error=True
        )

    def _safe_float_conversion(self, value):
        """Safely convert various input types to float."""
        try:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # Clean the string of non-numeric characters except decimal point and negative sign
                cleaned = ''.join(c for c in value if c.isdigit() or c in '.-')
                return float(cleaned) if cleaned else 0.0
            elif isinstance(value, dict) and 'value' in value:
                return self._safe_float_conversion(value['value'])
            return 0.0
        except Exception as e:
            logging.warning(f"Could not convert '{value}' to float: {str(e)}")
            return 0.0

    def _normalize_list_input(self, values):
        """Normalize input to ensure it's a list of numeric values."""
        # If input is a string that might be a serialized list/dict
        if isinstance(values, str):
            try:
                # Try to parse as JSON
                parsed = json.loads(values)
                if isinstance(parsed, list):
                    values = parsed
                elif isinstance(parsed, dict) and 'values' in parsed:
                    values = parsed['values']
                else:
                    # Single value as JSON
                    values = [parsed]
            except json.JSONDecodeError:
                # If not JSON, try comma-separated values
                if ',' in values:
                    values = [v.strip() for v in values.split(',')]
                else:
                    # Just a single value
                    values = [values]

        # If not a list at this point, make it one
        if not isinstance(values, list):
            values = [values]

        # Print input data for debugging
        print(f"Values before conversion: {values}")

        # Convert all values to float
        numeric_values = [self._safe_float_conversion(v) for v in values]
        print(f"Values after conversion: {numeric_values}")

        return numeric_values

    # Core calculation methods with numeric returns
    def calculate_total(self, values: List[Union[int, float, str]]) -> float:
        """Calculate the sum of a list of numerical values.

        Input: A list of values that can be integers, floats, or strings representing numbers.
        Example input: [100, 200, "300", 400.5] or "100, 200, 300, 400.5" or {"values": [100, 200, 300, 400.5]}
        Output: The sum as a float, rounded to 2 decimal places.
        Example output: 1000.50

        Use this tool when you need to calculate the total of multiple values, such as summing revenue across different periods or calculating total assets.
        """
        try:
            numeric_values = self._normalize_list_input(values)
            total = sum(numeric_values)
            print(f"Total calculated: {total}")
            return round(total, 2)
        except Exception as e:
            print(f"Error in calculate_total: {str(e)}")
            return 0.0

    def calculate_average(self, values: List[Union[int, float, str]]) -> float:
        """Calculate the arithmetic mean (average) of a list of numerical values.

        Input: A list of values that can be integers, floats, or strings representing numbers.
        Example input: [10, 20, "30", 40.5] or "10, 20, 30, 40.5" or {"values": [10, 20, 30, 40.5]}
        Output: The average as a float, rounded to 2 decimal places.
        Example output: 25.13

        Use this tool when you need to find the average of multiple values, such as calculating average monthly revenue, average inventory levels, or average expenses.
        """
        try:
            numeric_values = self._normalize_list_input(values)
            if not numeric_values:
                return 0.0
            avg = sum(numeric_values) / len(numeric_values)
            print(f"Average calculated: {avg}")
            return round(avg, 2)
        except Exception as e:
            print(f"Error in calculate_average: {str(e)}")
            return 0.0

    def calculate_percentage(self, part: Union[int, float, str], whole: Union[int, float, str]) -> float:
        """Calculate what percentage one value is of another value.

        Input: Two numerical values - part (the portion) and whole (the total).
        Example input: part=25, whole=100 or part="25", whole="100"
        Output: The percentage as a float, rounded to 2 decimal places.
        Example output: 25.00

        Use this tool for percentage calculations such as profit margins, growth rates, or portion analyses. For example, calculate what percentage gross profit is of revenue, or what percentage current liabilities are of total liabilities.
        """
        try:
            part_val = self._safe_float_conversion(part)
            whole_val = self._safe_float_conversion(whole)

            if whole_val == 0:
                print("Warning: Division by zero in percentage calculation")
                return 0.0

            percentage = (part_val / whole_val) * 100
            print(f"Percentage calculated: {percentage}%")
            return round(percentage, 2)
        except Exception as e:
            print(f"Error in calculate_percentage: {str(e)}")
            return 0.0

    def extract_values_by_year(self, data: Union[List[Dict], str], year_key: str = "year", value_key: str = "amount") -> Dict:
        """Aggregate financial data by year from a list of financial records.

        Input: 
        - data: A list of dictionaries, each containing financial records (can be a JSON string)
        - year_key: The dictionary key that contains the year information (default: "year")
        - value_key: The dictionary key that contains the value to be aggregated (default: "amount")

        Example input: 
        data=[{"year": "2020", "amount": 100}, {"year": "2020", "amount": 200}, {"year": "2021", "amount": 300}]
        year_key="year"
        value_key="amount"

        Output: A dictionary with years as keys and aggregated values as values.
        Example output: {"2020": 300, "2021": 300}

        Use this tool when you need to group and sum financial data by year, such as aggregating revenue, expenses, or other financial metrics across multiple entries for the same year.
        """
        try:
            # Parse data if it's a string
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {str(e)}")
                    return {}

            # Ensure data is a list
            if not isinstance(data, list):
                print(f"Expected list but got {type(data)}")
                return {}

            print(
                f"Processing {len(data)} records with year_key='{year_key}' and value_key='{value_key}'")

            aggregated = {}
            for entry in data:
                if not isinstance(entry, dict):
                    print(f"Skipping non-dict entry: {entry}")
                    continue

                year = entry.get(year_key)
                if year is None:
                    print(
                        f"Skipping entry without year_key '{year_key}': {entry}")
                    continue

                # Convert year to string to use as dict key
                year_str = str(year)

                # Get and convert value
                raw_value = entry.get(value_key, 0)
                value = self._safe_float_conversion(raw_value)

                # Aggregate
                aggregated[year_str] = aggregated.get(year_str, 0) + value

            print(f"Aggregated result: {aggregated}")
            return aggregated
        except Exception as e:
            print(f"Error in extract_values_by_year: {str(e)}")
            return {}

    def calculate_dupont_roe(self, npm: Union[int, float, str], at: Union[int, float, str], fl: Union[int, float, str]) -> float:
        """Calculate Return on Equity (ROE) using the DuPont formula.

        Input: Three values (can be numbers or strings):
        - npm: Net Profit Margin percentage (%)
        - at: Asset Turnover ratio
        - fl: Financial Leverage ratio

        Example input: npm=10.5, at=2.0, fl=1.5
        Output: ROE as a percentage (float), rounded to 2 decimal places.
        Example output: 31.50

        Use this tool when performing a DuPont analysis to understand the drivers of a company's ROE. This breaks down ROE into three components: profitability (npm), efficiency (at), and leverage (fl).
        """
        try:
            npm_val = self._safe_float_conversion(npm)
            at_val = self._safe_float_conversion(at)
            fl_val = self._safe_float_conversion(fl)

            # Calculate ROE using DuPont formula
            # We need to divide NPM by 100 since it's a percentage
            roe = (npm_val / 100) * at_val * fl_val * 100
            print(f"DuPont ROE calculated: {roe}%")
            return round(roe, 2)
        except Exception as e:
            print(f"Error in calculate_dupont_roe: {str(e)}")
            return 0.0

    def calculate_ratio(self, numerator: Union[int, float, str], denominator: Union[int, float, str]) -> float:
        """Calculate a financial ratio by dividing the numerator by the denominator.

        Input: Two values (can be numbers or strings):
        - numerator: The top number in the ratio
        - denominator: The bottom number in the ratio

        Example input: numerator=200, denominator=50
        Output: The ratio as a float value, rounded to 4 decimal places.
        Example output: 4.0000

        Use this tool for calculating any financial ratio, such as current ratio (current assets/current liabilities), debt-to-equity ratio (total debt/total equity), or price-to-earnings ratio (price per share/earnings per share).
        """
        try:
            num_val = self._safe_float_conversion(numerator)
            denom_val = self._safe_float_conversion(denominator)

            if denom_val == 0:
                print("Warning: Division by zero in ratio calculation")
                return 0.0

            ratio = num_val / denom_val
            print(f"Ratio calculated: {ratio}")
            return round(ratio, 4)
        except Exception as e:
            print(f"Error in calculate_ratio: {str(e)}")
            return 0.0

    def get_tools_metadata(self) -> tuple:
        descriptions = [f"{t.name}: {t.description}" for t in self.tools]
        names = [t.name for t in self.tools]
        return "\n".join(descriptions), ", ".join(names)
