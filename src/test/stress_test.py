import asyncio
import random
import time
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import DATABASE_URL
from src.core.models import ResourceOperation
from src.erase import clear_tables_and_reset_sequences
from src.test.insert_test import add_settlement, add_resources

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# Нагрузочное тестирование
async def main():
    await clear_tables_and_reset_sequences()
    async with AsyncSessionLocal() as session:
        settlement = await add_settlement(session)
        await add_resources(session, settlement)

        # Массовая вставка данных (10000 записей)
        operations = []
        for _ in range(10000):
            operation_type = random.choice(["consumption", "replenishment"])
            quantity = (
                random.randint(1, 500)
                if operation_type == "replenishment"
                else random.randint(-500, -1)
            )
            operations.append(
                ResourceOperation(
                    resource_id=1,
                    settlement_id=settlement.id,
                    date=datetime.now(),
                    quantity=quantity,
                    operation_type=operation_type,
                )
            )
        start_time = time.time()
        session.add_all(operations)
        await session.commit()
        elapsed_time = time.time() - start_time
        print(
            f"🚀 Нагрузочное тестирование завершено: 10 000 записей вставлено за {elapsed_time:.2f} секунд."
        )
    await clear_tables_and_reset_sequences()


if __name__ == "__main__":
    asyncio.run(main())
