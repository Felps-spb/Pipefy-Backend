from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.config.database import get_session
from app.modules.customers.clients.pipefy_client import PipefyClient
from app.modules.customers.repository.customer_repository import CustomerRepository
from app.modules.customers.repository.pipefy_event_repository import PipefyEventRepository
from app.modules.customers.services.customer_service import CustomerService



def get_service(session: AsyncSession = Depends(get_session)) -> CustomerService:
    repository = CustomerRepository(session)
    pipefy_event_repository = PipefyEventRepository(session)
    pipefy_client = PipefyClient()
    return CustomerService(repository, pipefy_client, pipefy_event_repository)
