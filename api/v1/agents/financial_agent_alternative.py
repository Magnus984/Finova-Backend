from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Dict, List, Any
import json


class FinancialOutput(BaseModel):
    """The structure for financial analysis output"""
    companyInfo: Dict[str, Any] = Field(
        description="Information about the company")
    incomeStatement: List[Dict[str, Any]] = Field(
        description="List of income statement line items")
    statementOfFinancialPosition: Dict[str, Any] = Field(
        description="Statement of financial position with assets, liabilities, and equity")
    dupontAnalysis: Dict[str, Any] = Field(
        description="DuPont analysis with ROE and ROA components")


class FinancialAgent:
    def __init__(self):
        # Initialize as before...

        # Use structured output agent for more reliable JSON
        self.agent_executor = self._create_structured_agent()

    def _create_structured_agent(self):
        prompt = PromptTemplate(
            template=get_financial_analysis_prompt(
                "{financial_data}", "{tools}", "{agent_scratchpad}", "{tool_names}"
            ),
            input_variables=["financial_data", "tools",
                             "agent_scratchpad", "tool_names"]
        )

        agent = create_structured_chat_agent(
            llm=self.llm,
            tools=self.tool_system.tools,
            prompt=prompt,
            output_schema=FinancialOutput
        )

        return AgentExecutor(
            agent=agent,
            tools=self.tool_system.tools,
            verbose=True,
            handle_parsing_errors=True
        )
