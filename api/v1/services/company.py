from fastapi import HTTPException
from api.v1.models.company import Company
from api.v1.schemas.company import CompanyCreate
from api.v1.models.user import User
from api.utils.logger import logger

class CompanyService:
    def create_company(self, company_data: CompanyCreate, current_user) -> dict:
        """
        Create a new company with the provided details.
        """
        # check for existing company
        existing_company = Company.objects(
        name=company_data.name,
        owner=current_user
        ).first()
        if existing_company:
            raise HTTPException(
                status_code=409,
                detail="Company already exists"
            )
        # Create new company document
        new_company = Company(
            name=company_data.name,
            size=company_data.size,
            business_email = company_data.business_email,
            business_phone = company_data.business_phone,
            address = company_data.address,
            industry = company_data.industry,
            owner=current_user
        )

        new_company.save()
        
        # Return the created company as a dictionary
        return new_company
    

    def get_company(self, company_id: str, current_user) -> dict:
        """
        Get a company by its ID.
        """
        exisiting_company = Company.objects(
            id=company_id,
            owner=current_user
            ).first()
        if not exisiting_company:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )
        return exisiting_company
    
    def list_companies(self, current_user) -> list:
        """
        List all companies for the current user.
        """
        try:
            # Query all companies owned by the current user
            companies = Company.objects(owner=current_user)

            # Convert each company to a dictionary
            return [company.to_dict() for company in companies]

        except Exception as e:
            logger.error(f"Error listing companies: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to list companies"
            )
    
company_service = CompanyService()