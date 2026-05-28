from abc import ABC, abstractmethod
from app.modules.customers.core.entities.customer import Customer
from app.modules.customers.http.dto.create_customer import CreateCustomerDTO


class ICustomerService(ABC):

    @abstractmethod
    async def create_customer(self, dto: CreateCustomerDTO) -> Customer: ...

    @abstractmethod
    async def get_customer_by_id(self, customer_id: int) -> Customer: ...

    @abstractmethod
    async def get_customer_by_email(self, email: str) -> Customer: ...

    @abstractmethod
    async def update_customer(self, customer_id: int, updated_data: dict) -> Customer | None: ...

    @abstractmethod
    async def delete_customer(self, customer_id: int) -> bool: ...