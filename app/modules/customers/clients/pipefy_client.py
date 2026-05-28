import logging
from typing import Any

from app.config.settings import settings
from app.modules.customers.core.entities.customer import Customer


logger = logging.getLogger(__name__)


CREATE_CARD_MUTATION = """
mutation CreateClientCard($input: CreateCardInput!) {
  createCard(input: $input) {
    card {
      id
      title
    }
    clientMutationId
  }
}
""".strip()


UPDATE_FIELDS_VALUES_MUTATION = """
mutation UpdateClientCardFields($input: UpdateFieldsValuesInput!) {
  updateFieldsValues(input: $input) {
    success
    updatedNode {
      ... on Card {
        id
      }
    }
  }
}
""".strip()


class PipefyClient:
    def build_create_card_payload(self, customer: Customer) -> dict[str, Any]:
        return {
            "query": CREATE_CARD_MUTATION,
            "variables": {
                "input": {
                    "pipe_id": settings.PIPEFY_PIPE_ID,
                    "title": customer.customer_name,
                    "fields_attributes": [
                        {
                            "field_id": settings.PIPEFY_FIELD_CLIENTE_NOME,
                            "field_value": customer.customer_name,
                        },
                        {
                            "field_id": settings.PIPEFY_FIELD_CLIENTE_EMAIL,
                            "field_value": customer.customer_email,
                        },
                        {
                            "field_id": settings.PIPEFY_FIELD_VALOR_PATRIMONIO,
                            "field_value": str(customer.patrimony_value),
                        },
                    ],
                }
            },
        }

    async def create_card(self, customer: Customer) -> dict[str, Any]:
        payload = self.build_create_card_payload(customer)
        logger.info("Simulating Pipefy createCard payload: %s", payload)
        return payload

    def build_update_card_payload(self, card_id: str, customer: Customer) -> dict[str, Any]:
        return {
            "query": UPDATE_FIELDS_VALUES_MUTATION,
            "variables": {
                "input": {
                    "nodeId": card_id,
                    "values": [
                        {
                            "fieldId": settings.PIPEFY_FIELD_STATUS,
                            "value": customer.customer_status.value,
                        },
                        {
                            "fieldId": settings.PIPEFY_FIELD_PRIORIDADE,
                            "value": customer.customer_priority.value,
                        },
                    ],
                }
            },
        }

    async def update_card_after_webhook(
        self,
        card_id: str,
        customer: Customer,
    ) -> dict[str, Any]:
        payload = self.build_update_card_payload(card_id, customer)
        logger.info("Simulating Pipefy updateFieldsValues payload: %s", payload)
        return payload
