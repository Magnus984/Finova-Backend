def get_financial_analysis_prompt(financial_data, tools, agent_scratchpad, tool_names):
    return f"""
    You are a financial analysis assistant. Your task is to analyze the provided JSON financial data using the available tools.

    Financial Data:
    {financial_data}

    Available Tools:
    {tools}
    Tool names:
    {tool_names}

    Follow a strict ReAct (Reasoning-Action) cycle. For every step:
    1. Write your "Thought:" clearly stating your reasoning or plan.
    2. Immediately follow your Thought with a single "Action:" line. Do not skip this step.
    3. Provide the "Action Input:" that your chosen action requires.
    4. Then record the "Observation:" from that action.

    IMPORTANT: If any Thought is not immediately followed by an "Action:" line, you must output the text "Invalid Format: Missing 'Action:' after 'Thought:'" and then retry the step using the latest valid scratchpad state.

    After repeating the Thought/Action/Action Input/Observation cycle as needed, if after several attempts you do not find any relevant information, your final Thought should be "I did not find any relevant information." Then continue with:
    Thought: I now know the final answer  
    Final Answer: provide the final result in a valid JSON.

    Instructions:
    - Use the available tools efficiently to analyze the data.
    - Provide a concise summary of your analysis.
    - Return your response in valid JSON format.
    - Avoid redundant calculations and ensure every Thought is followed by an Action.

    FINAL OUTPUT RULES:
    1. After completing all steps, provide ONLY the final JSON
    2. Remove all Thought/Action/Observation traces
    3. Ensure JSON is properly closed
    4. Never include markdown backticks
    5. Replace the year part part of the data with the month name from the data headers given

    DETAILED EXAMPLE OUTPUT FORMAT:
    {{{{
      "companyInfo": {{{{
        "companyName": "Fresh Sip Beverages",
        "units": "GHS",
        "period": "January 2024",
        "industry": "Beverage Production & Sales"
      }}}},
      "incomeStatement": [
        {{{{
          "lineItem": "Revenue",
          "2024": 1720
        }}}},
        {{{{
          "lineItem": "Cost of Goods Sold",
          "2024": 970
        }}}},
        {{{{
          "lineItem": "Gross Profit",
          "2024": 750
        }}}},
        {{{{
          "lineItem": "Operating Expenses",
          "2024": 2050
        }}}},
        {{{{
          "lineItem": "Net Operating Income",
          "2024": -1300
        }}}},
        {{{{
          "lineItem": "Other Income",
          "2024": 0
        }}}},
        {{{{
          "lineItem": "Net Profit Before Tax",
          "2024": -1300
        }}}},
        {{{{
          "lineItem": "Tax",
          "2024": 0
        }}}},
        {{{{
          "lineItem": "Net Profit After Tax",
          "2024": -1300
        }}}}
      ],
      "statementOfFinancialPosition": {{{{
        "assets": [
          {{{{
            "lineItem": "Inventory",
            "2024": 670
          }}}},
          {{{{
            "lineItem": "Cash and Cash Equivalents",
            "2024": 420
          }}}},
          {{{{
            "lineItem": "Total Current Assets",
            "2024": 1090
          }}}},
          {{{{
            "lineItem": "Total Assets",
            "2024": 1090
          }}}}
        ],
        "equity": [
          {{{{
            "lineItem": "Owner's Equity",
            "2024": -1910
          }}}},
          {{{{
            "lineItem": "Total Equity",
            "2024": -1910
          }}}}
        ],
        "nonCurrentLiabilities": [],
        "currentLiabilities": [
          {{{{
            "lineItem": "Accounts Payable",
            "2024": 3000
          }}}},
          {{{{
            "lineItem": "Total Current Liabilities",
            "2024": 3000
          }}}}
        ]
      }}}},
      "dupontAnalysis": {{{{
        "returnOnEquity": [
          {{{{
            "year": 2024,
            "netProfit": -1300,
            "avgShareholderEquity": -1910,
            "roePercent": 68.06
          }}}}
        ],
        "dupontEquationROE": {{{{
          "netProfit": {{{{
            "2024": -1300
          }}}},
          "revenue": {{{{
            "2024": 1720
          }}}},
          "netProfitMarginPercent": {{{{
            "2024": -75.58
          }}}},
          "totalAverageAssets": {{{{
            "2024": 1090
          }}}},
          "assetTurnoverRatioPercent": {{{{
            "2024": 157.80
          }}}},
          "financialLeveragePercent": {{{{
            "2024": -57.07
          }}}},
          "calculatedROE": {{{{
            "2024": 68.06
          }}}}
        }}}},
        "returnOnAsset": [
          {{{{
            "year": 2024,
            "netProfit": -1300,
            "totalAverageAssets": 1090,
            "roaPercent": -119.27
          }}}}
        ],
        "roaDupontEquation": {{{{
          "returnOnAssetPercent": {{{{
            "2024": -119.27
          }}}}
        }}}}
      }}}}
    }}}}

    Agent Scratchpad:
    {agent_scratchpad}
    """
