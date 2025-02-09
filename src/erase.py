import asyncio

import asyncpg
from rich.console import Console
from rich.panel import Panel

from src.config import DB_CONFIG, TABLES

# Настройки подключения к БД
console = Console()


async def clear_tables():
    conn = await asyncpg.connect(**DB_CONFIG)
    try:
        console.print(Panel("[bold cyan]Очистка всех таблиц...[/]", expand=False))

        for table in TABLES:
            await conn.execute(f"DELETE FROM {table} CASCADE;")
            console.print(f"[green]✔[/] Таблица [bold]{table}[/] очищена.")

        console.print(
            Panel("[bold green]✅ Все таблицы успешно очищены![/]", expand=False)
        )
    except Exception as e:
        console.print(f"[bold red]❌ Ошибка при очистке: {e}[/]")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(clear_tables())
