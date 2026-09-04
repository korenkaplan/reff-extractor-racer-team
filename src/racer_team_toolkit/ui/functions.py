import questionary
from rich.console import Console
from rich.panel import Panel

console = Console()


def select_menu(message: str, choices: list[str]) -> str:
    """Display a menu of choices and return the selected option."""
    return questionary.select(message, choices=choices).ask()


def select_menu_tuple(message: str, choices: list[str]) -> tuple[int, str]:
    """Display a menu and return the index and selected option."""

    selected = questionary.select(message, choices=choices).ask()
    index = choices.index(selected)

    return index, selected


def print_header(title: str) -> None:
    """Print a formatted header using rich."""
    console.print(Panel.fit(title))


def print_success(message: str) -> None:
    """Print a success message in green."""
    console.print(f"[green][V][/green] {message}")


def print_info(message: str) -> None:
    """Print an informational message in cyan."""
    console.print(f"[cyan][i][/cyan] {message}")


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    console.print(f"[yellow][!][/yellow] {message}")


def print_error(message: str) -> None:
    """Print an error message in red."""
    console.print(f"[red][-][/red] {message}")
