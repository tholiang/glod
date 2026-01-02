"""
GLOD Client Library - Rich formatting utilities for CLI output

Provides convenient functions for formatted console output.
"""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Initialize Rich console
console = Console()


def print_welcome():
    """Display welcome message"""
    welcome_text = Text.from_markup(
        "[bold cyan]GLOD[/bold cyan] - [yellow]AI Code Editor[/yellow]"
    )
    console.print(
        Panel(
            welcome_text,
            expand=False,
            border_style="cyan",
            padding=(1, 2),
        )
    )


def print_success(message: str):
    """Print success message"""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str):
    """Print error message"""
    console.print(f"[red]✗[/red] {message}")


def print_info(message: str):
    """Print info message"""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_response_header(title: str = "Agent Response"):
    """Print a nice header for agent response"""
    console.print()
    console.print(Panel.fit(f"[bold cyan]{title}[/bold cyan]", border_style="cyan"))


def print_response_footer():
    """Print a footer after agent response"""
    console.print()


def get_console() -> Console:
    """Get the Rich console instance"""
    return console

