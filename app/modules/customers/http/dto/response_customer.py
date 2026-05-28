from pydantic import BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Any
from app.modules.customers.core.entities.customer import CustomerPriority, CustomerStatus

class ResponseCustomerDTO(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: UUID
    customer_name: str = Field(alias="cliente_nome")
    customer_email: EmailStr = Field(alias="cliente_email")
    solicitation_type: str = Field(alias="tipo_solicitacao")
    patrimony_value: float = Field(alias="valor_patrimonio")
    customer_priority: CustomerPriority = Field(alias="prioridade")
    customer_status: CustomerStatus = Field(alias="status")
    created_at: datetime
    updated_at: datetime
    pipefy_card_payload: dict[str, Any]
