from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date


class BusinessInfo(BaseModel):
    """Basic business information"""
    name: str
    industry: Optional[str] = None
    location: Optional[str] = None
    business_type: Optional[str] = Field(
        None, description="Product-based, Service-based, or Mixed")
    currency: str = "GHS"
    established_date: Optional[str] = None


class FinancialRecord(BaseModel):
    """Base class for all financial records"""
    date: str
    amount: float
    description: Optional[str] = None
    category: Optional[str] = None


class SalesRecord(FinancialRecord):
    """Record for sales of products or services"""
    id: Optional[str] = None
    item_name: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    customer_type: Optional[str] = None
    payment_method: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2024-01-01",
                "item_name": "Fresh Pine Juice",
                "quantity": 45,
                "unit_price": 8.0,
                "amount": 360.0,
                "payment_method": "Mobile Money",
                "customer_type": "Retail",
                "category": "Beverage",
                "description": "Regular order"
            }
        }
    }


class ServiceRecord(FinancialRecord):
    """Record for service-based revenue"""
    id: Optional[str] = None
    service_name: str
    client: Optional[str] = None
    duration: Optional[str] = None
    payment_method: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2024-01-01",
                "service_name": "Consulting",
                "amount": 500.0,
                "client": "ABC Company",
                "duration": "2 hours",
                "payment_method": "Bank Transfer",
                "category": "Professional Services"
            }
        }
    }


class InventoryRecord(FinancialRecord):
    """Record for inventory purchases"""
    id: Optional[str] = None
    item_name: str
    quantity: Optional[str] = None
    unit_cost: Optional[float] = None
    supplier: Optional[str] = None
    payment_method: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2024-01-01",
                "item_name": "Pineapples",
                "quantity": "50 kg",
                "unit_cost": 6.0,
                "amount": 300.0,
                "supplier": "Local Farmer",
                "payment_method": "Mobile Money",
                "category": "Raw Materials"
            }
        }
    }


class ExpenseRecord(FinancialRecord):
    """Record for business expenses"""
    id: Optional[str] = None
    expense_type: str
    payment_method: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2024-01-01",
                "expense_type": "Rent",
                "amount": 1200.0,
                "payment_method": "Bank Transfer",
                "description": "Monthly shop rent",
                "category": "Operating Expense"
            }
        }
    }


class LiabilityRecord(FinancialRecord):
    """Record for business liabilities"""
    id: Optional[str] = None
    creditor: str
    due_date: Optional[str] = None
    payment_status: Optional[str] = None
    liability_type: Optional[str] = Field(
        None, description="Current or Non-current")

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2024-01-01",
                "creditor": "Supplier (Packaging Ltd)",
                "amount": 3000.0,
                "due_date": "2024-01-15",
                "payment_status": "Pending",
                "liability_type": "Current",
                "category": "Accounts Payable"
            }
        }
    }


class AssetRecord(FinancialRecord):
    """Record for business assets"""
    id: Optional[str] = None
    asset_name: str
    asset_type: Optional[str] = Field(
        None, description="Current or Non-current")
    depreciation: Optional[float] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2024-01-01",
                "asset_name": "Delivery Van",
                "amount": 50000.0,
                "asset_type": "Non-current",
                "depreciation": 5000.0,
                "category": "Vehicle",
                "description": "Used for product deliveries"
            }
        }
    }


class FinancialPeriod(BaseModel):
    """Time period for financial analysis"""
    start_date: str
    end_date: str
    previous_periods: Optional[int] = Field(
        1, description="Number of previous periods to include in analysis")


class FinancialAnalysisRequest(BaseModel):
    """Request model for financial analysis"""
    business_info: BusinessInfo
    period: FinancialPeriod
    sales_records: Optional[List[SalesRecord]] = []
    service_records: Optional[List[ServiceRecord]] = []
    inventory_records: Optional[List[InventoryRecord]] = []
    expense_records: Optional[List[ExpenseRecord]] = []
    liability_records: Optional[List[LiabilityRecord]] = []
    asset_records: Optional[List[AssetRecord]] = []

    model_config = {
        "json_schema_extra": {
            "example": {
                "business_info": {
                    "name": "Fresh Sip Beverages",
                    "industry": "Beverage Production & Sales",
                    "location": "Kumasi, Ghana",
                    "business_type": "Product-based",
                    "currency": "GHS"
                },
                "period": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31",
                    "previous_periods": 1
                },
                "sales_records": [
                    {
                        "date": "2024-01-01",
                        "item_name": "Fresh Pine Juice",
                        "quantity": 45,
                        "unit_price": 8.0,
                        "amount": 360.0,
                        "payment_method": "Mobile Money",
                        "customer_type": "Retail",
                        "category": "Beverage"
                    }
                ]
            }
        }
    }


# Response models
class CompanyInfo(BaseModel):
    """Company information in the response"""
    company_name: str
    units: str = "whole numbers"
    currency: str = "GHS"
    period: str


class IncomeStatementItem(BaseModel):
    """Line item in the income statement"""
    line_item: str
    values: Dict[str, Optional[float]]


class FinancialPositionItem(BaseModel):
    """Line item in the statement of financial position"""
    line_item: str
    values: Dict[str, Optional[float]]


class ROEAnalysis(BaseModel):
    """Return on Equity analysis"""
    year: int
    net_profit: float
    avg_shareholder_equity: float
    roe_percent: float


class ROAAnalysis(BaseModel):
    """Return on Assets analysis"""
    year: int
    net_profit: float
    total_average_assets: float
    roa_percent: float


class DupontEquationROE(BaseModel):
    """Components of the DuPont equation for ROE"""
    net_profit: Dict[str, float]
    revenue: Dict[str, float]
    net_profit_margin_percent: Dict[str, float]
    total_average_assets: Dict[str, float]
    asset_turnover_ratio_percent: Dict[str, float]
    financial_leverage_percent: Dict[str, float]
    calculated_roe: Dict[str, float]


class ROADupontEquation(BaseModel):
    """DuPont equation for ROA"""
    return_on_asset_percent: Dict[str, float]


class DupontAnalysis(BaseModel):
    """Complete DuPont analysis"""
    return_on_equity: List[ROEAnalysis]
    dupont_equation_roe: DupontEquationROE
    return_on_asset: List[ROAAnalysis]
    roa_dupont_equation: ROADupontEquation


class FinancialAnalysisResponse(BaseModel):
    """Response model for financial analysis"""
    company_info: CompanyInfo
    income_statement: List[IncomeStatementItem]
    statement_of_financial_position: Dict[str, List[FinancialPositionItem]]
    dupont_analysis: DupontAnalysis
