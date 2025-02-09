import asyncio
from datetime import datetime, timedelta
from rich.console import Console
from sqlalchemy import select, update, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import DATABASE_URL
from src.core.models import (
    Infrastructure,
    Notification,
    ResourceOperation,
    Resource,
    SensorDevice,
    Task,
    Settlement,
)

# Setup Async SQLAlchemy engine and session
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

console = Console()


async def get_settlement(session: AsyncSession, settlement_name: str) -> int:
    """Get an existing settlement ID."""
    try:
        # Try to find an existing settlement
        result = await session.execute(
            select(Settlement.id).where(Settlement.name == settlement_name)
        )
        settlement_id = result.scalar()
        return settlement_id
    except SQLAlchemyError as e:
        console.print(f"[bold red]Error getting settlement:[/bold red] {str(e)}")
        await session.rollback()  # Rollback the transaction
        raise


async def ensure_infrastructure_exists(
    session: AsyncSession, infrastructure_id: int, settlement_id: int
):
    try:
        infrastructure_exists = await session.execute(
            select(Infrastructure.id).filter(Infrastructure.id == infrastructure_id)
        )
        if not infrastructure_exists.scalar():
            # Create new infrastructure record if it doesn't exist
            new_infrastructure = Infrastructure(
                id=infrastructure_id,
                name=f"Infrastructure {infrastructure_id}",
                type="Default Type",  # Example type
                settlement_id=settlement_id,
            )
            session.add(new_infrastructure)
            await session.commit()
    except SQLAlchemyError as e:
        console.print(
            f"[bold red]Error ensuring infrastructure exists:[/bold red] {str(e)}"
        )
        await session.rollback()  # Rollback the transaction


async def test_energy_consumption_trigger():
    try:
        async with AsyncSessionLocal() as session:
            # Get or create a settlement
            settlement_name = "Arctic Base"
            settlement_id = await get_settlement(session, settlement_name)

            # Ensure infrastructure exists
            await ensure_infrastructure_exists(session, 1, settlement_id)

            # Insert a new sensor device
            sensor = SensorDevice(
                name="Test Sensor",
                type="IoT",
                infrastructure_id=1,
                status="active",
                last_update=datetime.now(),
                energy_consumption=501,
            )
            session.add(sensor)
            await session.commit()

            # Verify if notification was created
            notification_count = await session.execute(
                select(func.count()).where(
                    Notification.type == "critical",
                    Notification.message.like("%Превышение %"),
                )
            )
            count = notification_count.scalar()
            console.print(
                f"[bold green]✅ Energy Consumption Trigger:[/bold green] Notifications for high energy consumption: {count}"
            )
    except SQLAlchemyError as e:
        console.print(
            f"[bold red]Error in energy consumption trigger:[/bold red] {str(e)}"
        )
        await session.rollback()  # Rollback the transaction


async def test_overdue_task_trigger():
    try:
        async with AsyncSessionLocal() as session:
            # Insert a new task with a past deadline
            task = Task(
                name="Test Overdue Task",
                description="This is a test task",
                status="pending",
                assignee="Technician",
                deadline=datetime.now() - timedelta(days=1),  # Past deadline
            )
            session.add(task)
            await session.commit()

            # Simulate task status update to 'overdue'
            await session.execute(
                update(Task).where(Task.id == task.id).values(status="overdue")
            )
            await session.commit()

            # Verify the expected outcome, e.g., notification for overdue task
            notification_count = await session.execute(
                select(func.count()).where(
                    Notification.type == "alert",
                    Notification.message.like("%просрочена и передана%"),
                )
            )
            count = notification_count.scalar()
            console.print(
                f"[bold yellow]⚠️ Overdue Task Trigger:[/bold yellow] Notifications for overdue tasks: {count}"
            )
    except SQLAlchemyError as e:
        console.print(f"[bold red]Error in overdue task trigger:[/bold red] {str(e)}")
        await session.rollback()  # Rollback the transaction


async def test_resource_threshold_trigger():
    async with AsyncSessionLocal() as session:
        try:
            settlement_name = "Arctic Base"
            settlement_id = await get_settlement(session, settlement_name)

            # Create a resource operation with valid values
            resource_operation = ResourceOperation(
                resource_id=2,
                settlement_id=settlement_id,
                quantity=-5000,  # Assuming negative quantity for consumption
                operation_type="consumption",  # Ensure this is a valid type
            )
            session.add(resource_operation)
            await session.commit()

            # Verify if notification was created for critical resource threshold
            notification_count = await session.execute(
                select(func.count()).where(
                    Notification.type == "warning",
                    Notification.message.like(f"%Критический уровень ресурса ID:%"),
                )
            )
            count = notification_count.scalar()
            console.print(
                f"[bold red]❗ Resource Threshold Trigger:[/bold red] Notifications for critical resource level: {count}"
            )

        except SQLAlchemyError as e:
            console.print(
                f"[bold red]Error in resource threshold trigger:[/bold red] {str(e)}"
            )
            await session.rollback()  # Rollback the transaction


async def main():
    console.print("[bold cyan]Running Trigger Tests[/bold cyan]")
    await test_energy_consumption_trigger()
    await test_overdue_task_trigger()
    await test_resource_threshold_trigger()
    console.print("[bold cyan]All Tests Completed[/bold cyan]")


if __name__ == "__main__":
    asyncio.run(main())
