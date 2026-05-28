from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class CustomerStatus(Enum):
    AWAITING_ANALYSIS = "Aguardando Análise"
    PROCESSED = "Processado"

class CustomerPriority(Enum):
    NORMAL = "prioridade_normal"
    HIGH = "prioridade_alta"    

@dataclass(slots=True)
class Customer:
    customer_name: str
    customer_email: str
    solicitation_type: str
    patrimony_value: float
    id: UUID = field(default_factory=uuid4)
    customer_status: CustomerStatus = CustomerStatus.AWAITING_ANALYSIS
    customer_priority: CustomerPriority = CustomerPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


    async def update_priority(self) -> None:
        if self.patrimony_value >= 200_000:
            self.customer_priority = CustomerPriority.HIGH
        else:
            self.customer_priority = CustomerPriority.NORMAL
        self.updated_at = datetime.now()

    async def mark_as_processed(self) -> None:
        self.customer_status = CustomerStatus.PROCESSED
        self.updated_at = datetime.now()
    
    async def is_processed(self) -> bool:
        return self.customer_status == CustomerStatus.PROCESSED
