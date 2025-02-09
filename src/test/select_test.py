import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from rich.console import Console
from rich.table import Table

from src.config import DATABASE_URL
from src.core.models import (
    EnergySystem,
    Event,
    GeoZone,
    Incident,
    Infrastructure,
    LogisticRoute,
    Notification,
    Personnel,
    ResourceOperation,
    ResourcePlan,
    Resource,
    Route,
    SensorDevice,
    Settlement,
    Task,
    TransportVehicle,
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def main():
    async with AsyncSessionLocal() as session:
        console = Console()
        models = [
            EnergySystem,
            Event,
            GeoZone,
            Incident,
            Infrastructure,
            LogisticRoute,
            Notification,
            Personnel,
            ResourceOperation,
            ResourcePlan,
            Resource,
            Route,
            SensorDevice,
            Settlement,
            Task,
            TransportVehicle,
        ]

        for model in models:
            result = await session.execute(select(model))
            rows = result.scalars().all()  # Use scalars() to get ORM objects

            table = Table(title=f"Data from {model.__tablename__}")

            # Add columns based on the model's attributes
            for column in model.__table__.columns:
                table.add_column(column.name)

            # Add rows to the table
            for row in rows:
                table.add_row(
                    *[
                        str(getattr(row, column.name))
                        for column in model.__table__.columns
                    ]
                )

            console.print(table)


if __name__ == "__main__":
    asyncio.run(main())
