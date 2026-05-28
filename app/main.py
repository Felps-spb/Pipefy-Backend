from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.config.database import create_db
from app.modules.customers.http.controllers.customer_controller import (
    router as customer_router,
)
from app.modules.customers.http.controllers.pipefy_webhook_controller import (
    router as pipefy_webhook_router,
)


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")

    await create_db()

    yield

    logger.info("Shutting down application...")


app = FastAPI(
    title="Pipefy Backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(customer_router)
app.include_router(pipefy_webhook_router)

