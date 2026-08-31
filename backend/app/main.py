from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app.api.customers import router as customers_router
from app.api.customer_locations import router as customer_locations_router


app = FastAPI(
    title="OM Recycling Asset Manager",
    version="0.1.0",
)

app.include_router(customers_router)
app.include_router(customer_locations_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
def database_health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"status": "ok", "database": "connected"}