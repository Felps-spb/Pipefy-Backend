from datetime import timezone

from app.modules.customers.repository.models.pipefy_event_model import PipefyEventModel
from sqlmodel.ext.asyncio.session import AsyncSession


class PipefyEventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_event_id(self, event_id: str) -> PipefyEventModel | None:
        return await self.session.get(PipefyEventModel, event_id)

    async def create_event(
        self,
        event_id: str,
        card_id: str,
        cliente_email: str,
        timestamp,
    ) -> PipefyEventModel:
        if timestamp.tzinfo is not None:
            timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)

        event = PipefyEventModel(
            event_id=event_id,
            card_id=card_id,
            cliente_email=cliente_email,
            timestamp=timestamp,
        )

        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)

        return event
