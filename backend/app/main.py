from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app.api.customers import router as customers_router
from app.api.customer_locations import router as customer_locations_router
from app.api.collections import router as collections_router
from app.api.collection_statuses import router as collection_statuses_router
from app.api.collection_items import router as collection_items_router
from app.api.assets import router as assets_router
from app.api.asset_inspections import router as asset_inspections_router
from app.api.intake import router as intake_router
from app.api.data_sanitization import router as data_sanitization_router
from app.api.asset_processing import router as asset_processing_router
from app.api.asset_dispositions import router as asset_dispositions_router
from app.api.asset_returns import router as asset_returns_router


app = FastAPI(
    title="OM Recycling Asset Manager",
    version="0.1.0",
)

app.include_router(customers_router)
app.include_router(customer_locations_router)
app.include_router(collections_router)
app.include_router(collection_statuses_router)
app.include_router(collection_items_router)
app.include_router(assets_router)
app.include_router(asset_inspections_router)
app.include_router(intake_router)
app.include_router(data_sanitization_router)
app.include_router(asset_processing_router)
app.include_router(asset_dispositions_router)
app.include_router(asset_returns_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
def database_health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"status": "ok", "database": "connected"}
