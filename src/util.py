from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

# Initialize Rich console
console = Console()


# Formatting Utilities
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


def print_help():
    """Display help with all available commands"""
    help_table = Table(title="Available Commands", show_header=True, header_style="bold cyan")
    help_table.add_column("Command", style="yellow", width=25)
    help_table.add_column("Description", width=50)
    
    help_table.add_row("/allow <path>", "Add a directory to allowed file access paths")
    help_table.add_row("/clear", "Clear message history with the agent")
    help_table.add_row("/server start", "Start the agent server")
    help_table.add_row("/server stop", "Stop the agent server")
    help_table.add_row("/server restart", "Restart the agent server")
    help_table.add_row("/server status", "Check agent server status")
    help_table.add_row("/help", "Show this help message")
    help_table.add_row("/exit", "Exit the program")
    
    console.print()
    console.print(help_table)
    console.print()
