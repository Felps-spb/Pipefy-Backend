from app.modules.customers.core.entities.customer import CustomerPriority, CustomerStatus
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4

class CustomerModel(SQLModel, table=True):
    __tablename__ = "customers"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    customer_name: str
    customer_email: str
    solicitation_type: str
    patrimony_value: float
    customer_status: CustomerStatus = Field(default=CustomerStatus.AWAITING_ANALYSIS)
    customer_priority: CustomerPriority = Field(default=CustomerPriority.NORMAL)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


