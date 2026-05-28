from fastapi import APIRouter, Depends, HTTPException, status
from app.modules.customers.http.dto.create_customer import CreateCustomerDTO
from app.modules.customers.http.dto.response_customer import ResponseCustomerDTO
from app.modules.customers.http.dependencies.dependencies import get_service
from app.modules.customers.services.customer_service import CustomerService
from app.modules.customers.core.exceptions.exceptions import CustomerAlreadyExistsException
from dataclasses import asdict

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("/", response_model=ResponseCustomerDTO, status_code=status.HTTP_201_CREATED)
async def create_customer(
    dto: CreateCustomerDTO,
    service: CustomerService = Depends(get_service),
):
    try:
        result = await service.create_customer(dto)
        return ResponseCustomerDTO(
            **asdict(result.customer),
            pipefy_card_payload=result.pipefy_card_payload,
        )
    except CustomerAlreadyExistsException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
