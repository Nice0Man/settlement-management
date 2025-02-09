import asyncio
import random
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.core.models import ResourceOperation, Incident, Notification, SensorDevice
from src.config import DATABASE_URL, CRITICAL_THRESHOLD, ENERGY_LIMIT

# Создание асинхронного движка SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# 1. Тестирование триггера контроля уровня ресурсов
async def test_resource_threshold():
    async with AsyncSessionLocal() as session:
        # Вставляем операцию потребления, чтобы снизить уровень ресурса ниже порога
        operation = ResourceOperation(
            resource_id=1,
            settlement_id=1,
            date=datetime.now(),
            quantity=-100,
            operation_type="consumption",
        )
        session.add(operation)
        await session.commit()

        # Проверяем, появилось ли уведомление
        result = await session.execute(
            "SELECT COUNT(*) FROM notifications WHERE type = 'warning' AND message LIKE '%ресурса ID: 1%'"
        )
        count = result.scalar()
        print(f"✅ Контроль уровня ресурсов: Уведомлений о низком ресурсе: {count}")


# 2. Тестирование обновления статуса инцидента
async def test_incident_resolution():
    async with AsyncSessionLocal() as session:
        # Создаем инцидент
        incident = Incident(
            type="Авария",
            description="Проблемы с энергией",
            status="open",
            resource_id=1,
        )
        session.add(incident)
        await session.commit()

        # Пополняем ресурс
        operation = ResourceOperation(
            resource_id=1,
            settlement_id=1,
            date=datetime.utcnow(),
            quantity=200,
            operation_type="replenishment",
        )
        session.add(operation)
        await session.commit()

        # Проверяем статус инцидента
        result = await session.execute(
            "SELECT status FROM incidents WHERE resource_id = 1"
        )
        status = result.scalar()
        print(
            f"✅ Автоматическое обновление инцидента: Статус после пополнения: {status}"
        )


# 3. Тестирование контроля потребления энергии
async def test_energy_control():
    async with AsyncSessionLocal() as session:
        # Обновляем данные устройства с превышением лимита потребления
        await session.execute(
            "UPDATE sensors_devices SET energy_consumption = 600 WHERE id = 1"
        )
        await session.commit()

        # Проверяем уведомление
        result = await session.execute(
            "SELECT COUNT(*) FROM notifications WHERE type = 'critical' AND message LIKE '%устройством ID: 1%'"
        )
        count = result.scalar()
        print(f"✅ Контроль потребления энергии: Уведомлений о превышении: {count}")


# Запуск всех тестов
async def run_tests():
    await test_resource_threshold()
    await test_incident_resolution()
    await test_energy_control()


if __name__ == "__main__":
    asyncio.run(run_tests())
