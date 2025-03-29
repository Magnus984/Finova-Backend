from typing import List, Dict, Union, Any
from api.v1.tools.calculation_tools import FinancialCalculationTools
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from templates.prompts.financial_analysis import get_financial_analysis_prompt
from pydantic import BaseModel, ValidationError
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import HumanMessage, SystemMessage
import json
import re
from api.core.config import settings


class FinancialAnalysisRequest(BaseModel):
    data: Dict[str, Any]


class FinancialAnalysisResponse:
    def __init__(self, data: dict):
        self.data = data


class FinancialOutput(BaseModel):
    companyInfo: dict
    incomeStatement: list
    statementOfFinancialPosition: dict
    dupontAnalysis: dict


class FinancialAgent:
    def __init__(self):
        self.llm = ChatAnthropic(
            model_name="claude-3-7-sonnet-20250219",
            temperature=0,
        )
        # Creating a helper LLM with a simpler model for JSON extraction
        self.json_extractor_llm = ChatAnthropic(
            model_name="claude-3-haiku-20240307",  # Using a lighter model for extraction
            temperature=0
        )
        self.tool_system = FinancialCalculationTools(self.llm)
        self.parser = JsonOutputParser(pydantic_object=FinancialOutput)
        self.agent_executor = self._create_agent()

    def _create_agent(self):
        prompt = PromptTemplate(
            template=get_financial_analysis_prompt(
                "{financial_data}", "{tools}", "{agent_scratchpad}", "{tool_names}"
            ),
            input_variables=["financial_data", "tools",
                             "agent_scratchpad", "tool_names"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            }
        )

        agent = create_tool_calling_agent(
            self.llm, self.tool_system.tools, prompt)

        return AgentExecutor(
            agent=agent,
            tools=self.tool_system.tools,
            verbose=True,
            handle_parsing_errors=self._handle_parsing_error,
            return_intermediate_steps=True
        )

    def _handle_parsing_error(self, error: OutputParserException) -> str:
        return f"""
        ERROR: {str(error)}
        Please reformat your response using:
        {FinancialOutput.model_json_schema(indent=2)}
        Remember:
        - Use double quotes
        - Numbers without quotes
        - Validate with tools
        - Provide ONLY the JSON object, nothing else before or after
        """

    async def _extract_json_with_llm(self, text: Any) -> Dict[str, Any]:
        """
        Use a specialized LLM to extract and fix JSON from text.
        """
        # Convert text to string if it's not already
        if not isinstance(text, str):
            try:
                # Try to convert to JSON string
                text = json.dumps(text)
            except:
                text = str(text)

        # Create a prompt for the JSON extractor
        system_prompt = """
        You are a specialized JSON extraction assistant. Your task is to:
        
        1. Extract valid JSON from the given text.
        2. Fix any syntax errors in the JSON.
        3. Return ONLY the fixed, valid JSON object with no additional text, comments, or explanations.
        
        The JSON should match this schema:
        {
          "companyInfo": {
            "companyName": string,
            "units": string,
            "period": string,
            "industry": string
          },
          "incomeStatement": [
            {
              "lineItem": string,
              year: number
            }
          ],
          "statementOfFinancialPosition": {
            "assets": array,
            "equity": array,
            "nonCurrentLiabilities": array,
            "currentLiabilities": array
          },
          "dupontAnalysis": {
            "returnOnEquity": array,
            "dupontEquationROE": object,
            "returnOnAsset": array,
            "roaDupontEquation": object
          }
        }
        
        If the input doesn't contain valid JSON, construct a minimal valid JSON object that matches the schema.
        """

        # Create messages for the extractor
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=f"Extract and fix the JSON from this text:\n\n{text}")
        ]

        # Get the response
        response = await self.json_extractor_llm.ainvoke(messages)
        extracted_text = response.content

        # Try to parse the extracted text
        try:
            # First try to directly parse as JSON
            return json.loads(extracted_text)
        except json.JSONDecodeError:
            # If direct parsing fails, look for JSON pattern
            json_pattern = re.compile(r'```(?:json)?\s*([\s\S]*?)\s*```')
            match = json_pattern.search(extracted_text)
            if match:
                try:
                    return json.loads(match.group(1))
                except:
                    pass

            # Last resort: find first { and last }
            first_brace = extracted_text.find('{')
            last_brace = extracted_text.rfind('}')
            if first_brace != -1 and last_brace != -1:
                try:
                    json_str = extracted_text[first_brace:last_brace+1]
                    return json.loads(json_str)
                except:
                    pass

        # If all extraction attempts fail, return a template object
        return self._create_template_json()

    def _create_template_json(self) -> Dict[str, Any]:
        """
        Create a template JSON object matching the expected schema.
        """
        return {
            "companyInfo": {
                "companyName": "Unknown",
                "units": "Unknown",
                "period": "Unknown",
                "industry": "Unknown"
            },
            "incomeStatement": [],
            "statementOfFinancialPosition": {
                "assets": [],
                "equity": [],
                "nonCurrentLiabilities": [],
                "currentLiabilities": []
            },
            "dupontAnalysis": {
                "returnOnEquity": [],
                "dupontEquationROE": {},
                "returnOnAsset": [],
                "roaDupontEquation": {}
            }
        }

    async def analyze_financial_data(self, request: FinancialAnalysisRequest) -> FinancialAnalysisResponse:
        try:
            tool_desc, tool_names = self.tool_system.get_tools_metadata()

            result = await self.agent_executor.ainvoke({
                "financial_data": json.dumps(request.data),
                "tools": tool_desc,
                "tool_names": tool_names,
                "agent_scratchpad": [],
            })

            # Extract output from the result
            output = result.get("output")

            # Print debugging info
            if isinstance(output, str):
                print(f"Raw output from agent (string): {output[:200]}...")
            else:
                print(
                    f"Raw output from agent (type {type(output)}): {str(output)[:200]}...")

            # Use LLM for extraction
            print("Using LLM for JSON extraction...")
            extracted_json = await self._extract_json_with_llm(output)

            # Try to validate the extracted JSON
            try:
                validated = FinancialOutput(**extracted_json).dict()
                return FinancialAnalysisResponse(data=validated)
            except ValidationError:
                # If validation fails, still use what we found
                return FinancialAnalysisResponse(data=extracted_json)

            # If direct extraction fails, try extracting from intermediate steps
            steps = result.get("intermediate_steps", [])
            if steps:
                print(
                    f"Found {len(steps)} intermediate steps, extracting from last few steps...")
                # Look at the last few steps, focusing on the ones most likely to contain the final result
                for step in reversed(steps):
                    # Get the output from the step
                    step_output = step.get("output", "") if isinstance(
                        step, dict) else step

                    # Extract with LLM
                    step_json = await self._extract_json_with_llm(step_output)
                    if step_json:
                        try:
                            validated = FinancialOutput(**step_json).dict()
                            return FinancialAnalysisResponse(data=validated)
                        except ValidationError:
                            # If validation fails, still use what we found
                            return FinancialAnalysisResponse(data=step_json)

            # If all extraction attempts fail
            return FinancialAnalysisResponse(data={"error": "Failed to extract valid financial analysis"})

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error during analysis: {str(e)}\n{error_trace}")
            return FinancialAnalysisResponse(data={"error": str(e)})
