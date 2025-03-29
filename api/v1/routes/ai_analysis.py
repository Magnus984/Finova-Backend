from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..schemas.response_models import SuccessResponse, ErrorResponse
from ..agents.financial_agent import FinancialAgent, FinancialAnalysisRequest, FinancialAnalysisResponse

router = APIRouter()
financial_agent = FinancialAgent()


@router.post("/analyze",
             )
async def analyze_financial_data(request: Dict[str, Any]):
    """Analyze financial data to generate comprehensive financial statements and DuPont analysis.

    This endpoint processes raw financial data to generate three main components:
    1. Income Statement - Shows revenue, expenses, and profitability over time
    2. Statement of Financial Position - Details assets, liabilities, and equity
    3. DuPont Analysis - Breaks down financial performance metrics (ROE, ROA)

    The frontend can send any valid JSON structure containing financial data.
    See documentation for example request and response formats.
    """
    try:
        # Wrap the raw dictionary in our request model
        analysis_request = FinancialAnalysisRequest(data=request)

        # Process the data
        analysis = await financial_agent.analyze_financial_data(analysis_request)

        return SuccessResponse(
            status_code=200,
            message="Financial analysis completed successfully",
            data=analysis.data
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
