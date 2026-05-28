from app.modules.customers.core.entities.customer import Customer
from app.modules.customers.core.interfaces.repository import ICustomerRepository
from app.modules.customers.core.interfaces.service import ICustomerService
from app.modules.customers.core.exceptions.exceptions import (
    CustomerAlreadyExistsException,
    CustomerNotFoundException,
)
from app.modules.customers.clients.pipefy_client import PipefyClient
from app.modules.customers.http.dto.pipefy_webhook import PipefyCardUpdatedWebhookDTO
from app.modules.customers.http.dto.create_customer import CreateCustomerDTO
from app.modules.customers.repository.pipefy_event_repository import PipefyEventRepository
from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass(slots=True)
class CreateCustomerResult:
    customer: Customer
    pipefy_card_payload: dict[str, Any]


@dataclass(slots=True)
class ProcessPipefyWebhookResult:
    customer: Customer
    event_id: str
    card_id: str
    already_processed: bool
    pipefy_update_payload: dict[str, Any] | None = None


class CustomerService(ICustomerService):
    def __init__(
        self,
        repository: ICustomerRepository,
        pipefy_client: PipefyClient,
        pipefy_event_repository: PipefyEventRepository,
    ):
        self.repository = repository
        self.pipefy_client = pipefy_client
        self.pipefy_event_repository = pipefy_event_repository

    async def create_customer(self, dto: CreateCustomerDTO) -> CreateCustomerResult:
        existing = await self.repository.get_customer_by_email(dto.customer_email)
        if existing:
            raise CustomerAlreadyExistsException(dto.customer_email)

        customer = Customer(
            customer_name=dto.customer_name,
            customer_email=dto.customer_email,
            solicitation_type=dto.solicitation_type,
            patrimony_value=dto.patrimony_value,
        )
        await customer.update_priority()

        created_customer = await self.repository.create_customer(customer)
        pipefy_card_payload = await self.pipefy_client.create_card(created_customer)

        return CreateCustomerResult(
            customer=created_customer,
            pipefy_card_payload=pipefy_card_payload,
        )

    async def get_customer_by_id(self, customer_id: UUID) -> Customer:
        customer = await self.repository.get_customer_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundException(customer_id)
        return customer

    async def get_customer_by_email(self, email: str) -> Customer:
        customer = await self.repository.get_customer_by_email(email)
        if not customer:
            raise CustomerNotFoundException(email)
        return customer

    async def process_pipefy_card_updated(
        self,
        dto: PipefyCardUpdatedWebhookDTO,
    ) -> ProcessPipefyWebhookResult:
        customer = await self.repository.get_customer_by_email(dto.cliente_email)
        if not customer:
            raise CustomerNotFoundException(dto.cliente_email)

        existing_event = await self.pipefy_event_repository.get_by_event_id(dto.event_id)
        if existing_event:
            return ProcessPipefyWebhookResult(
                customer=customer,
                event_id=dto.event_id,
                card_id=dto.card_id,
                already_processed=True,
            )

        await customer.update_priority()
        await customer.mark_as_processed()

        updated_customer = await self.repository.update_customer(
            customer.id,
            {
                "customer_status": customer.customer_status,
                "customer_priority": customer.customer_priority,
                "updated_at": customer.updated_at,
            },
        )

        await self.pipefy_event_repository.create_event(
            event_id=dto.event_id,
            card_id=dto.card_id,
            cliente_email=dto.cliente_email,
            timestamp=dto.timestamp,
        )

        pipefy_update_payload = await self.pipefy_client.update_card_after_webhook(
            dto.card_id,
            updated_customer,
        )

        return ProcessPipefyWebhookResult(
            customer=updated_customer,
            event_id=dto.event_id,
            card_id=dto.card_id,
            already_processed=False,
            pipefy_update_payload=pipefy_update_payload,
        )
    
    async def update_customer(self, customer_id: UUID, updated_data: dict) -> Customer:
        customer = await self.repository.get_customer_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundException(customer_id)

        for key, value in updated_data.items():
            setattr(customer, key, value)

        if "patrimony_value" in updated_data:
            await customer.update_priority()
            updated_data["customer_priority"] = customer.customer_priority
            updated_data["updated_at"] = customer.updated_at

        return await self.repository.update_customer(customer_id, updated_data)
    
    async def delete_customer(self, customer_id: UUID) -> None:
        customer = await self.repository.get_customer_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundException(customer_id)

        await self.repository.delete_customer(customer_id)
