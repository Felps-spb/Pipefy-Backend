from dataclasses import replace

import pytest

from app.modules.customers.clients.pipefy_client import PipefyClient
from app.modules.customers.core.entities.customer import (
    Customer,
    CustomerPriority,
    CustomerStatus,
)
from app.modules.customers.http.dto.create_customer import CreateCustomerDTO
from app.modules.customers.http.dto.pipefy_webhook import PipefyCardUpdatedWebhookDTO
from app.modules.customers.services.customer_service import CustomerService


class InMemoryCustomerRepository:
    def __init__(self):
        self.customers_by_email = {}
        self.created_customers = []
        self.update_count = 0

    async def create_customer(self, customer):
        self.customers_by_email[customer.customer_email] = customer
        self.created_customers.append(customer)
        return customer

    async def get_customer_by_id(self, customer_id):
        for customer in self.customers_by_email.values():
            if customer.id == customer_id:
                return customer
        return None

    async def get_customer_by_email(self, email):
        return self.customers_by_email.get(email)

    async def update_customer(self, customer_id, updated_data):
        customer = await self.get_customer_by_id(customer_id)
        if not customer:
            return None

        for key, value in updated_data.items():
            setattr(customer, key, value)

        self.update_count += 1
        return customer

    async def delete_customer(self, customer_id):
        customer = await self.get_customer_by_id(customer_id)
        if not customer:
            return False

        del self.customers_by_email[customer.customer_email]
        return True


class InMemoryPipefyEventRepository:
    def __init__(self):
        self.events_by_id = {}

    async def get_by_event_id(self, event_id):
        return self.events_by_id.get(event_id)

    async def create_event(self, event_id, card_id, cliente_email, timestamp):
        event = {
            "event_id": event_id,
            "card_id": card_id,
            "cliente_email": cliente_email,
            "timestamp": timestamp,
        }
        self.events_by_id[event_id] = event
        return event


def make_service(customer_repository=None, event_repository=None):
    return CustomerService(
        customer_repository or InMemoryCustomerRepository(),
        PipefyClient(),
        event_repository or InMemoryPipefyEventRepository(),
    )


@pytest.mark.asyncio
async def test_create_customer_with_valid_payload_saves_customer():
    customer_repository = InMemoryCustomerRepository()
    service = make_service(customer_repository=customer_repository)
    dto = CreateCustomerDTO(
        cliente_nome="João Silva",
        cliente_email="joao.silva@example.com",
        tipo_solicitacao="Atualização cadastral",
        valor_patrimonio=250000,
    )

    result = await service.create_customer(dto)

    saved_customer = customer_repository.customers_by_email["joao.silva@example.com"]
    assert result.customer == saved_customer
    assert saved_customer.customer_status == CustomerStatus.AWAITING_ANALYSIS
    assert saved_customer.customer_priority == CustomerPriority.HIGH
    assert result.pipefy_card_payload["variables"]["input"]["title"] == "João Silva"


@pytest.mark.asyncio
async def test_webhook_processes_customer_and_applies_priority_rule():
    customer_repository = InMemoryCustomerRepository()
    customer = Customer(
        customer_name="João Silva",
        customer_email="joao.silva@example.com",
        solicitation_type="Atualização cadastral",
        patrimony_value=199999.99,
    )
    await customer_repository.create_customer(customer)
    service = make_service(customer_repository=customer_repository)
    dto = PipefyCardUpdatedWebhookDTO(
        event_id="evt_123",
        card_id="card_456",
        cliente_email="joao.silva@example.com",
        timestamp="2026-05-18T12:00:00Z",
    )

    result = await service.process_pipefy_card_updated(dto)

    assert result.already_processed is False
    assert result.customer.customer_status == CustomerStatus.PROCESSED
    assert result.customer.customer_priority == CustomerPriority.NORMAL
    assert result.pipefy_update_payload["variables"]["input"]["values"] == [
        {"fieldId": "status", "value": "Processado"},
        {"fieldId": "prioridade", "value": "prioridade_normal"},
    ]


@pytest.mark.asyncio
async def test_webhook_does_not_reprocess_duplicate_event_id():
    customer_repository = InMemoryCustomerRepository()
    event_repository = InMemoryPipefyEventRepository()
    customer = Customer(
        customer_name="João Silva",
        customer_email="joao.silva@example.com",
        solicitation_type="Atualização cadastral",
        patrimony_value=250000,
    )
    await customer_repository.create_customer(customer)
    service = make_service(
        customer_repository=customer_repository,
        event_repository=event_repository,
    )
    dto = PipefyCardUpdatedWebhookDTO(
        event_id="evt_123",
        card_id="card_456",
        cliente_email="joao.silva@example.com",
        timestamp="2026-05-18T12:00:00Z",
    )

    first_result = await service.process_pipefy_card_updated(dto)
    customer_after_first_event = replace(first_result.customer)
    second_result = await service.process_pipefy_card_updated(dto)

    assert first_result.already_processed is False
    assert second_result.already_processed is True
    assert second_result.pipefy_update_payload is None
    assert customer_repository.update_count == 1
    assert second_result.customer.customer_status == customer_after_first_event.customer_status
    assert second_result.customer.customer_priority == customer_after_first_event.customer_priority
