import argparse
from abc import ABC, abstractmethod
from typing import Optional, Dict, Callable

from rich.console import Console


class Base(ABC):
    """
    Base class for rich-based CLI applications.

    Provides argument parsing, a rich console, and a structured execution flow.
    """

    def __init__(self, description: str = "A Rich CLI Application", console: Optional[Console] = None) -> None:
        """
        Initializes the CLI application.

        Args:
            description: The application's description, displayed in help.
        """
        self._parser = argparse.ArgumentParser(description=description)
        self._console = console or Console()  # Use provided console or create a default one
        self._interactive_commands: Dict[str, Callable[[str], None]] = {}
        self.add_arguments()
        self.add_interactive_commands()

    @property
    def console(self) -> Console:
        """Provides access to the rich console object."""
        return self._console

    def add_arguments(self) -> None:
        """
        Adds command-line arguments to the parser.
        """
        self._parser.add_argument(
            "-i", "--interactive", action="store_true", help="Run in interactive mode after initial execution."
        )

    def add_interactive_commands(self) -> None:
        self.register_interactive_command("quit", self._quit_interactive, help_text="Exit the interactive mode.")
        self.register_interactive_command("help", self._help_interactive, help_text="Show this help message.")

    def register_interactive_command(self, command_name: str, command_func: Callable[[str], None], help_text: str = ""):
        if command_name in self._interactive_commands:
            raise ValueError(f"Command '{command_name}' already registered")
        self._interactive_commands[command_name] = command_func
        # self._interactive_commands[command_name].help = help_text

    def _quit_interactive(self, args: str) -> None:
        """Exits interactive mode."""
        self._running = False

    def _help_interactive(self, args: str) -> None:
        """Prints help for interactive mode."""
        self.console.print("[bold]Available interactive commands:[/bold]")
        for name, func in self._interactive_commands.items():
            self.console.print(f"  [cyan]{name}[/cyan]: {getattr(func, 'help', 'No help available')}")

    @abstractmethod
    def run(self, args: argparse.Namespace) -> int:
        """
        The main logic of the CLI application.  Subclasses MUST implement this.

        Args:
            args: The parsed command-line arguments.

        Returns:
            An integer representing the application's exit code (0 for success).
        """
        raise NotImplementedError("Subclasses must implement the 'run' method.")

    def main(self) -> int:
        """
        The main entry point for the CLI application. Handles argument parsing,
        exception handling, and calls the `run` method.
        """
        try:
            args = self._parser.parse_args()
            return self.run(args)
        except Exception as e:
            self._console.print(f"[bold red]Error:[/bold red] {e}")
            return 1
