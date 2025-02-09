import asyncio
import random
import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

from rich.console import Console

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

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
console = Console()


async def populate_database():
    async with AsyncSessionLocal() as session:
        console.print("[bold cyan]Заполняем базу данных...[/bold cyan]")

        # Populate Settlements
        settlement = Settlement(
            name="Arctic Base", region="North Pole", climate_type="Arctic"
        )
        session.add(settlement)
        await session.commit()
        console.print("[green]✔ Поселение добавлено[/green]")

        # Populate Infrastructure
        infrastructure = Infrastructure(
            name="Solar Power Plant", type="Energy", settlement_id=settlement.id
        )
        session.add(infrastructure)
        await session.commit()
        console.print("[green]✔ Инфраструктура добавлена[/green]")

        # Populate Resources
        resources = [
            Resource(
                name="Water", unit="Liters", type="Liquid", settlement_id=settlement.id
            ),
            Resource(name="Food", unit="Kg", type="Solid", settlement_id=settlement.id),
            Resource(
                name="Fuel", unit="Liters", type="Liquid", settlement_id=settlement.id
            ),
        ]
        session.add_all(resources)
        await session.commit()
        console.print("[green]✔ Ресурсы добавлены[/green]")

        # Populate Resource Operations

        operation_type = random.choice(["consumption", "replenishment"])
        quantity = (
            random.randint(1, 500)
            if operation_type == "replenishment"
            else random.randint(-500, -1)
        )

        operations = [
            ResourceOperation(
                resource_id=res.id,
                settlement_id=settlement.id,
                date=datetime.datetime.now(),
                quantity=quantity,
                operation_type=operation_type,
            )
            for res in resources
            for _ in range(5)
        ]
        session.add_all(operations)
        await session.commit()
        console.print("[green]✔ Операции с ресурсами добавлены[/green]")

        # Populate Sensor Devices
        sensor = SensorDevice(
            name="Temperature Sensor",
            type="IoT",
            infrastructure_id=infrastructure.id,
            status="active",
            last_update=datetime.datetime.now(),
            energy_consumption=5,
        )
        session.add(sensor)
        await session.commit()
        console.print("[green]✔ Датчики добавлены[/green]")

        # Populate Incidents
        incident = Incident(
            type="Power Failure",
            description="Power outage detected",
            date_time=datetime.datetime.now(),
            status="open",
            resource_id=resources[0].id,
        )
        session.add(incident)
        await session.commit()
        console.print("[green]✔ Инциденты добавлены[/green]")

        # Populate Tasks
        task = Task(
            name="Check Energy Levels",
            description="Verify power supply status",
            status="pending",
            assignee="Technician",
            deadline=datetime.datetime.now() + datetime.timedelta(days=3),
        )
        session.add(task)
        await session.commit()
        console.print("[green]✔ Задачи добавлены[/green]")

        # Populate Personnel
        personnel = Personnel(
            full_name="John Doe",
            position="Engineer",
            infrastructure_id=infrastructure.id,
        )
        session.add(personnel)
        await session.commit()
        console.print("[green]✔ Персонал добавлен[/green]")

        # Populate Events
        event = Event(
            name="Annual Maintenance",
            date=datetime.datetime.now(),
            event_type="Maintenance",
            settlement_id=settlement.id,
        )
        session.add(event)
        await session.commit()
        console.print("[green]✔ События добавлены[/green]")

        # Populate Transport Vehicles
        vehicle = TransportVehicle(
            name="Supply Truck",
            type="Truck",
            status="available",  # Ensure this is one of the allowed statuses
            current_location=func.ST_GeomFromText(
                "POINT(0 0)", 4326
            ),  # Use ST_GeomFromText for geometry
            fuel_reserve=100,
        )
        session.add(vehicle)
        await session.commit()
        console.print("[green]✔ Транспортные средства добавлены[/green]")

        # Populate Logistic Routes
        logistic_route = LogisticRoute(
            name="Supply Route",
            description="Route for supply deliveries",
            waypoints=func.ST_GeomFromText(
                "LINESTRING(0 0, 1 1)"
            ),  # Convert WKT to geometry
            status="active",
        )
        session.add(logistic_route)
        await session.commit()
        console.print("[green]✔ Логистические маршруты добавлены[/green]")

        # Populate Resource Plans
        plan = ResourcePlan(
            name="Water Conservation Plan",
            description="Plan to conserve water resources",
            start_date=datetime.datetime.now(),
            end_date=datetime.datetime.now() + datetime.timedelta(days=30),
            resource_id=resources[0].id,
        )
        session.add(plan)
        await session.commit()
        console.print("[green]✔ Планы ресурсов добавлены[/green]")

        # Populate Routes
        route = Route(
            name="Emergency Evacuation Route",
            description="Route for emergency evacuations",
            waypoints=func.ST_GeomFromText(
                "LINESTRING(0 0, 1 1)"
            ),  # Convert WKT to geometry
            status="active",
        )
        session.add(route)
        await session.commit()
        console.print("[green]✔ Маршруты добавлены[/green]")

        # Populate Notifications
        notification = Notification(
            type="Alert",
            message="Severe weather warning",
            timestamp=datetime.datetime.now(),
            status="unread",
        )
        session.add(notification)
        await session.commit()
        console.print("[green]✔ Уведомления добавлены[/green]")

        # Populate GeoZones
        geozone = GeoZone(
            name="Protected Area",
            type="Conservation",
            coordinates="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",  # Example geometry
            description="Area protected for conservation",
            usage_type="Restricted",
        )
        session.add(geozone)
        await session.commit()
        console.print("[green]✔ Геозоны добавлены[/green]")

        # Populate Energy Systems
        energy_system = EnergySystem(
            name="Wind Turbine",
            type="Renewable",
            capacity=1500,
            current_load=500,
            status="operational",
            infrastructure_id=infrastructure.id,
        )
        session.add(energy_system)
        await session.commit()
        console.print("[green]✔ Энергетические системы добавлены[/green]")

        console.print("[bold cyan]База данных успешно заполнена![/bold cyan]")


if __name__ == "__main__":
    asyncio.run(populate_database())
