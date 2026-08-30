# OM Recycling Asset Manager

Open-source asset lifecycle management software for an e-waste collection,
refurbishment, inventory, and resale operation.

## Purpose

The system tracks IT equipment from initial collection through:

- Customer collection
- Receiving
- Asset identification
- Inspection
- Data destruction
- Refurbishment
- Parts consumption
- Quality control
- Warehouse inventory
- Sale
- Warranty
- Complete asset history

## Core Principle

Every physical asset receives a unique Asset ID.

The Asset ID remains associated with the asset throughout its complete lifecycle.

## Technology

- Python
- FastAPI
- PostgreSQL
- React
- TypeScript
- Docker
- Redis
- Alembic

All core application components are intended to use open-source software.

## Development

Development is containerized using Docker so that the environment can be
reproduced at different development locations.

See `DEVELOPMENT.md` for development instructions.

## Project Status

See `PROJECT_STATUS.md`.