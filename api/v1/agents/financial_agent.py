from langchain.agents import create_react_agent, AgentExecutor
# from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from typing import Dict, Any
from api.core.config import settings
from ..tools.calculation_tools import FinancialCalculationTools
from pydantic import BaseModel
from templates.prompts.financial_analysis import get_financial_analysis_prompt
import json


class FinancialAnalysisRequest(BaseModel):
    """Simple request model that accepts any JSON data"""
    data: Dict[str, Any]


class FinancialAnalysisResponse:
    def __init__(self, data: dict):
        self.data = data

    def to_json(self):
        return json.dumps(self.data, indent=2)


class FinancialAgent:
    def __init__(self):
        # Initialize the LLM first
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model_name="gpt-4o",
        )

        # Initialize tools system with LLM dependency
        self.financial_tools = FinancialCalculationTools(llm=self.llm)

        # Get tool instances and metadata
        self.tool_instances = self.financial_tools.tools
        self.tool_descriptions, self.tool_names = self.financial_tools.get_tools_metadata()

        # Configure the prompt template
        self.prompt = PromptTemplate(
            template=get_financial_analysis_prompt(
                "{financial_data}", "{tools}", "{agent_scratchpad}", "{tool_names}"
            ),
            input_variables=["financial_data", "tools",
                             "agent_scratchpad", "tool_names"]
        )

        # Create the agent with integrated tools
        self.agent_executor = self._create_agent_executor()

    def _create_agent_executor(self) -> AgentExecutor:
        """Configure and return the agent executor"""
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tool_instances,
            prompt=self.prompt
        )

        return AgentExecutor(
            agent=agent,
            tools=self.tool_instances,
            verbose=True,
            handle_parsing_errors=True,
            output_parser=JsonOutputParser()
        )

    async def analyze_financial_data(self, request: FinancialAnalysisRequest) -> FinancialAnalysisResponse:
        """Execute financial analysis with integrated tools"""
        try:
            agent_input = {
                "financial_data": request.data,
                "tools": self.tool_descriptions,
                "agent_scratchpad": "",
                "tool_names": self.tool_names
            }

            result = await self.agent_executor.ainvoke(agent_input)
            return FinancialAnalysisResponse(data=result.get("output", {}))

        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            print(f"ERROR: {error_msg}")
            return FinancialAnalysisResponse(data={"error": error_msg})
