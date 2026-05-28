from fastapi import APIRouter, Depends, HTTPException, status

from app.modules.customers.core.exceptions.exceptions import CustomerNotFoundException
from app.modules.customers.http.dependencies.dependencies import get_service
from app.modules.customers.http.dto.pipefy_webhook import (
    PipefyCardUpdatedWebhookDTO,
    PipefyCardUpdatedWebhookResponseDTO,
)
from app.modules.customers.services.customer_service import CustomerService


router = APIRouter(prefix="/webhooks/pipefy", tags=["Pipefy Webhooks"])


@router.post(
    "/card-updated",
    response_model=PipefyCardUpdatedWebhookResponseDTO,
    status_code=status.HTTP_200_OK,
)
async def pipefy_card_updated(
    dto: PipefyCardUpdatedWebhookDTO,
    service: CustomerService = Depends(get_service),
):
    try:
        result = await service.process_pipefy_card_updated(dto)
        return PipefyCardUpdatedWebhookResponseDTO(
            event_id=result.event_id,
            card_id=result.card_id,
            cliente_email=result.customer.customer_email,
            already_processed=result.already_processed,
            status=result.customer.customer_status,
            prioridade=result.customer.customer_priority,
            pipefy_update_payload=result.pipefy_update_payload,
        )
    except CustomerNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
