from typing import Optional

import Geometry
from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    Text,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from geoalchemy2 import Geometry

Base = declarative_base()


class EnergySystem(Base):
    __tablename__ = "energy_systems"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    current_load: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    infrastructure_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("infrastructure.id")
    )


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    settlement_id: Mapped[int] = mapped_column(Integer, ForeignKey("settlements.id"))


class GeoZone(Base):
    __tablename__ = "geozones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    coordinates: Mapped[Geometry] = mapped_column(Geometry("POLYGON"), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    usage_type: Mapped[str] = mapped_column(String(50), nullable=False)


class Incident(Base):
    __tablename__ = "incidents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Text] = mapped_column(Text, nullable=False)
    date_time: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[int] = mapped_column(Integer, ForeignKey("resources.id"))


class Infrastructure(Base):
    __tablename__ = "infrastructure"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    settlement_id: Mapped[int] = mapped_column(Integer, ForeignKey("settlements.id"))


class LogisticRoute(Base):
    __tablename__ = "logistic_routes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Text] = mapped_column(Text, nullable=False)
    waypoints: Mapped[Text] = mapped_column(Text)  # Assuming geometry is stored as text
    status: Mapped[str] = mapped_column(String(50), nullable=False)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[Text] = mapped_column(Text, nullable=False)
    timestamp: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)


class Personnel(Base):
    __tablename__ = "personnel"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[str] = mapped_column(String(50), nullable=False)
    infrastructure_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("infrastructure.id")
    )


class ResourceOperation(Base):
    __tablename__ = "resource_operations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resource_id: Mapped[int] = mapped_column(Integer, ForeignKey("resources.id"))
    settlement_id: Mapped[int] = mapped_column(Integer, ForeignKey("settlements.id"))
    date: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    operation_type: Mapped[str] = mapped_column(String(20), nullable=False)


class ResourcePlan(Base):
    __tablename__ = "resource_plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Text] = mapped_column(Text, nullable=False)
    start_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    resource_id: Mapped[int] = mapped_column(Integer, ForeignKey("resources.id"))


class Resource(Base):
    __tablename__ = "resources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    settlement_id: Mapped[int] = mapped_column(Integer, ForeignKey("settlements.id"))


class Route(Base):
    __tablename__ = "routes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Text] = mapped_column(Text, nullable=False)
    waypoints: Mapped[Text] = mapped_column(Text)  # Assuming geometry is stored as text
    status: Mapped[str] = mapped_column(String(50), nullable=False)


class SensorDevice(Base):
    __tablename__ = "sensors_devices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    infrastructure_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("infrastructure.id")
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    last_update: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    energy_consumption: Mapped[int] = mapped_column(Integer, nullable=False)


class Settlement(Base):
    __tablename__ = "settlements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    climate_type: Mapped[str] = mapped_column(String(50), nullable=False)


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Text] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    assignee: Mapped[str] = mapped_column(String(100), nullable=False)
    deadline: Mapped[DateTime] = mapped_column(DateTime, nullable=False)


class TransportVehicle(Base):
    __tablename__ = "transport_vehicles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    current_location: Mapped[Text] = mapped_column(
        Text
    )  # Assuming geometry is stored as text
    fuel_reserve: Mapped[int] = mapped_column(Integer, nullable=False)
