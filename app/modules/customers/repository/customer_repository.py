from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from dataclasses import asdict
from uuid import UUID

from app.modules.customers.core.entities.customer import Customer
from app.modules.customers.core.interfaces.repository import ICustomerRepository
from app.modules.customers.repository.models.customer_model import CustomerModel


class CustomerRepository(ICustomerRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_model(self, customer: Customer) -> CustomerModel:
        return CustomerModel(**asdict(customer))

    def _to_entity(self, model: CustomerModel) -> Customer:
        return Customer(
            id=model.id,
            customer_name=model.customer_name,
            customer_email=model.customer_email,
            solicitation_type=model.solicitation_type,
            patrimony_value=model.patrimony_value,
            customer_status=model.customer_status,
            customer_priority=model.customer_priority,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def create_customer(self, customer: Customer) -> Customer:
        model = self._to_model(customer)

        self.session.add(model)

        await self.session.commit()
        await self.session.refresh(model)

        return self._to_entity(model)
    
    async def get_customer_by_id(self, customer_id: UUID) -> Customer | None:
        result = await self.session.exec(
            select(CustomerModel).where(CustomerModel.id == customer_id)
        )

        model = result.first()

        return self._to_entity(model) if model else None
    
    async def get_customer_by_email(self, email: str) -> Customer | None:
        result = await self.session.exec(
            select(CustomerModel).where(CustomerModel.customer_email == email)
        )

        model = result.first()

        return self._to_entity(model) if model else None
    
    async def update_customer(self, customer_id: UUID, updated_data: dict) -> Customer | None:
        result = await self.session.exec(
            select(CustomerModel).where(CustomerModel.id == customer_id)
        )

        model = result.first()

        if not model:
            return None

        for key, value in updated_data.items():
            setattr(model, key, value)

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        return self._to_entity(model)
    
    async def delete_customer(self, customer_id: UUID) -> bool:
        result = await self.session.exec(
            select(CustomerModel).where(CustomerModel.id == customer_id)
        )

        model = result.first()

        if not model:
            return False

        await self.session.delete(model)
        await self.session.commit()

        return True
