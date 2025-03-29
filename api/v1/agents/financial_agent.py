from typing import List, Dict, Union, Any
from api.v1.tools.calculation_tools import FinancialCalculationTools
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from templates.prompts.financial_analysis import get_financial_analysis_prompt
from pydantic import BaseModel, ValidationError
from langchain_core.exceptions import OutputParserException
import json
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
        self.llm = ChatOpenAI(
            model_name="gpt-4o-mini",
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
        """

    async def analyze_financial_data(self, request: FinancialAnalysisRequest) -> FinancialAnalysisResponse:
        try:
            tool_desc, tool_names = self.tool_system.get_tools_metadata()

            for attempt in range(3):
                result = await self.agent_executor.ainvoke({
                    "financial_data": json.dumps(request.data),
                    "tools": tool_desc,
                    "tool_names": tool_names,
                    "agent_scratchpad": []
                })

                if output := result.get("output"):
                    try:
                        parsed = self.parser.parse(output)
                        return FinancialAnalysisResponse(parsed)
                    except ValidationError as e:
                        print(
                            f"Validation error (attempt {attempt+1}): {str(e)}")

            return FinancialAnalysisResponse({"error": "Max validation attempts failed"})

        except Exception as e:
            return FinancialAnalysisResponse({"error": str(e)})
