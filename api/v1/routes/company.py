from fastapi import APIRouter, Depends, HTTPException
import json

company = APIRouter(prefix="/company", tags=["Company"])
from api.v1.schemas.response_models import (
    SuccessResponse, ErrorResponse, ErrorData
)
from api.v1.schemas.company import CompanyCreate, CompanyResponse
from api.v1.services.company import company_service
from api.v1.services.user import user_service
from api.v1.models.user import User
from api.utils.logger import logger

@company.post(
    "/create",
    response_model=SuccessResponse[CompanyResponse],
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Bad Request"
        },
        409: {
            "model": ErrorResponse,
            "description": "Conflict"
        }
    }
)
def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(user_service.get_current_user)
) -> SuccessResponse:
    """
    Create a new company with the provided details.
    """
    try:
        # Create new company
        new_company = company_service.create_company(company_data, current_user)
 
        return SuccessResponse(
            status_code=201,
            message="Company created successfully",
            data=new_company
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error creating company: {str(e)}")
        return ErrorResponse(
            status_code=500,
            message="Failed to create company",
            data=ErrorData(error=str(e), error_type=type(e).__name__)
        )
    

@company.get(
    "/get",
     response_model=SuccessResponse[CompanyResponse],
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Bad Request"
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found"
        }
    }
)
def get_company(
    company_id: str,
    current_user: User = Depends(user_service.get_current_user),
) -> SuccessResponse:
    """
    Get company details by ID.
    """
    try:
        # Get company by ID
        company = company_service.get_company(company_id, current_user)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return SuccessResponse(
            status_code=200,
            message="Company retrieved successfully",
            data=company
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error retrieving company: {str(e)}")
        return ErrorResponse(
            status_code=500,
            message="Failed to retrieve company",
            data=ErrorData(error=str(e), error_type=type(e).__name__)
        )
    
@company.get(
    "/list",
    response_model=SuccessResponse[list[CompanyResponse]],
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Bad Request"
        },
        404: {
            "model": ErrorResponse,
            "description": "Not Found"
        }
    }
)
def list_companies(
    current_user: User = Depends(user_service.get_current_user)
) -> SuccessResponse:
    """
    List all companies of the current user.
    """
    try:
        # Get all companies
        companies = company_service.list_companies(current_user)
        return SuccessResponse(
            status_code=200,
            message="Companies retrieved successfully",
            data=companies
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error listing companies: {str(e)}")
        return ErrorResponse(
            status_code=500,
            message="Failed to list companies",
            data=ErrorData(error=str(e), error_type=type(e).__name__)
        )