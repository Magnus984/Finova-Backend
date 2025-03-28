from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from main import app
import pytest
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi import FastAPI

client = TestClient(app)

def test_http_exception(client):
    """Test HTTP exception handler"""
    @app.get("/test-http-error")
    async def test_endpoint():
        raise HTTPException(status_code=404, detail="Item not found")

    response = client.get("/test-http-error")
    assert response.status_code == 404
    assert response.json() == {
        "status": "error",
        "status_code": 404,
        "message": "Item not found",
        "data": None
    }

def test_validation_error(client):
    """Test validation error handler"""
    @app.post("/test-validation")
    async def validation_endpoint(item_id: int):
        return {"item_id": item_id}

    response = client.post("/test-validation", json={"item_id": "not_an_integer"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    json_response = response.json()
    assert json_response["status"] == "error"
    assert json_response["status_code"] == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert json_response["message"] == "Validation error"
    assert "errors" in json_response["data"]


# def test_global_exception(client):
#     """Test global exception handler"""
#     @app.get("/test-global-error")
#     async def error_endpoint():
#         raise ValueError("Test error")

#     response = client.get("/test-global-error")
#     json_response = response.json()
#     print(json_response)
#     assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
#     assert json_response["status"] == "error"
#     assert json_response["status_code"] == status.HTTP_500_INTERNAL_SERVER_ERROR
#     assert json_response["message"] == "An internal server error occurred"
#     assert json_response["data"]["error_type"] == "ValueError"