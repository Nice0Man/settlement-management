import asyncio
import importlib
from rich.console import Console
from rich.table import Table

# Список модулей тестов (указываем полные пути относительно корня проекта)
TEST_MODULES = [
    "src.test.insert_test",
    "src.test.triggers_test",
    # "src.test.select_test",
    "src.test.stress_test",
]

console = Console()


async def run_all_tests():
    results = []  # для накопления результатов тестов
    for mod_name in TEST_MODULES:
        console.rule(f"[bold cyan]Запуск теста: {mod_name}[/bold cyan]")
        try:
            mod = importlib.import_module(mod_name)
            # Предполагается, что в каждом модуле реализована функция main(), возвращающая awaitable
            if hasattr(mod, "main"):
                await mod.main()
                console.print(f"[green]✔ Тест {mod_name} успешно выполнен[/green]")
                results.append((mod_name, "Успешно"))
            else:
                console.print(
                    f"[yellow]⚠ В модуле {mod_name} не найдено определение 'main'[/yellow]"
                )
                results.append((mod_name, "Не найдено 'main'"))
        except Exception as e:
            console.print(f"[red]✖ Тест {mod_name} завершился с ошибкой: {e}[/red]")
            results.append((mod_name, f"Ошибка: {e}"))

    # Вывод сводной таблицы результатов
    table = Table(title="Результаты тестирования")
    table.add_column("Модуль", style="cyan", no_wrap=True)
    table.add_column("Статус", style="magenta")
    for mod, status in results:
        table.add_row(mod, status)

    console.print(table)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
