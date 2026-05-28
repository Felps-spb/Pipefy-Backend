from datetime import datetime

from sqlmodel import Field, SQLModel


class PipefyEventModel(SQLModel, table=True):
    __tablename__ = "pipefy_events"

    event_id: str = Field(primary_key=True)
    card_id: str
    cliente_email: str
    timestamp: datetime
    processed_at: datetime = Field(default_factory=datetime.now)
