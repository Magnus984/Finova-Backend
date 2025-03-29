from langchain.tools import tool
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Dict
from api.core.config import settings


class DatabaseTools:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.DB_URI)
        self.db = self.client[settings.DB_NAME]

    @tool
    async def get_historical_financial_data(self, company_id: str, period: str) -> Optional[Dict]:
        """Retrieve historical financial data from the database"""
        collection = self.db.financial_data
        return await collection.find_one({
            "company_id": company_id,
            "period": period
        })
