import asyncio
import time
from datetime import datetime
import random

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.core.models import ResourceOperation
from src.config import DATABASE_URL

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# Нагрузочное тестирование
async def stress_test():
    async with AsyncSessionLocal() as session:
        start_time = time.time()

        # Массовая вставка данных (10000 записей)
        operations = [
            ResourceOperation(
                resource_id=1,
                settlement_id=1,
                date=datetime.now(),
                quantity=-random.randint(10, 500),
                operation_type="consumption",
            )
            for _ in range(10000)
        ]
        session.add_all(operations)
        await session.commit()

        elapsed_time = time.time() - start_time
        print(
            f"🚀 Нагрузочное тестирование завершено: 10 000 записей вставлено за {elapsed_time:.2f} секунд."
        )


if __name__ == "__main__":
    asyncio.run(stress_test())
