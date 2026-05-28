from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr

from app.modules.customers.core.entities.customer import CustomerPriority, CustomerStatus


class PipefyCardUpdatedWebhookDTO(BaseModel):
    event_id: str
    card_id: str
    cliente_email: EmailStr
    timestamp: datetime


class PipefyCardUpdatedWebhookResponseDTO(BaseModel):
    event_id: str
    card_id: str
    cliente_email: EmailStr
    already_processed: bool
    status: CustomerStatus
    prioridade: CustomerPriority
    pipefy_update_payload: dict[str, Any] | None = None
