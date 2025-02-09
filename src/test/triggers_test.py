import asyncio
from datetime import datetime

from rich.console import Console
from sqlalchemy import select, exists, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.core.models import (
    ResourceOperation,
    Incident,
    Resource,
    Settlement,
    Notification,
)
from src.config import DATABASE_URL

# Create an asynchronous SQLAlchemy engine
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

console = Console()


# Helper function to ensure settlement exists
async def ensure_settlement_exists(session: AsyncSession, settlement_id: int):
    # Check if the settlement already exists
    settlement_exists = await session.execute(
        select(exists().where(Settlement.id == settlement_id))
    )
    if not settlement_exists.scalar():
        # Create a new settlement with default values
        new_settlement = Settlement(
            id=settlement_id,
            name=f"Settlement {settlement_id}",
            region="Default Region",  # Provide a default non-NULL value
            climate_type="Temperate",  # Provide a default non-NULL value
        )
        session.add(new_settlement)
        await session.commit()


# Helper function to ensure resource exists
async def ensure_resource_exists(
    session: AsyncSession, resource_id: int, settlement_id: int
):
    await ensure_settlement_exists(session, settlement_id)
    resource_exists = await session.execute(
        select(exists().where(Resource.id == resource_id))
    )
    if not resource_exists.scalar():
        # Insert the resource if it doesn't exist
        resource = Resource(
            id=resource_id,
            name=f"Resource {resource_id}",
            unit="default_unit",  # Provide a default non-NULL value
            type="default_type",  # Provide a default non-NULL value
            settlement_id=settlement_id,
        )
        session.add(resource)
        await session.commit()


# Test resource threshold trigger
async def test_resource_threshold():
    async with AsyncSessionLocal() as session:
        await ensure_resource_exists(session, 1, 1)

        # Insert a consumption operation to lower the resource level below the threshold
        operation = ResourceOperation(
            resource_id=1,
            settlement_id=1,
            date=datetime.now(),
            quantity=-100,
            operation_type="consumption",
        )
        session.add(operation)
        await session.commit()

        # Check if a notification was created
        notification_count = await session.execute(
            select(func.count()).where(
                Notification.type == "warning",
                Notification.message.like("%ресурса ID: 1%"),
            )
        )
        count = notification_count.scalar()
        console.print(
            f"[bold green]✅ Resource Threshold Control:[/bold green] Notifications for low resource: {count}"
        )


# Run all tests
async def run_tests():
    console.print("[bold cyan]Running Trigger Tests[/bold cyan]")
    await test_resource_threshold()
    console.print("[bold cyan]All Tests Completed[/bold cyan]")


if __name__ == "__main__":
    asyncio.run(run_tests())
