import asyncio
import asyncpg
from rich.console import Console
from rich.panel import Panel

from src.config import DB_CONFIG, TABLES

# Настройки подключения к БД
console = Console()


async def clear_tables_and_reset_sequences():
    conn = await asyncpg.connect(**DB_CONFIG)
    try:
        console.print(
            Panel(
                "[bold cyan]Очистка всех таблиц и сброс последовательностей...[/]",
                expand=False,
            )
        )

        for table in TABLES:
            # Clear the table
            await conn.execute(f"DELETE FROM {table} CASCADE;")
            console.print(f"[green]✔[/] Таблица [bold]{table}[/] очищена.")
            sequence_name = f"{table}_id_seq"
            await conn.execute(f"ALTER SEQUENCE {sequence_name} RESTART WITH 1;")
            console.print(
                f"[green]✔[/] Последовательность [bold]{sequence_name}[/] сброшена."
            )

        console.print(
            Panel(
                "[bold green]✅ Все таблицы и последовательности успешно очищены и сброшены![/]",
                expand=False,
            )
        )
    except Exception as e:
        console.print(f"[bold red]❌ Ошибка при очистке: {e}[/]")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(clear_tables_and_reset_sequences())
