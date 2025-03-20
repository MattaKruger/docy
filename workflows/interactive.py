import argparse
from base import CLIBase


class MyInteractiveCLI(CLIBase):
    def __init__(self):
        super().__init__(description="My Interactive CLI App")
        self._data = []

    def add_arguments(self):
        super().add_arguments()
        self._parser.add_argument("-n", "--name", help="Your name", default="World")

    def add_interactive_commands(self):
        super().add_interactive_commands()
        self.register_interactive_command("add", self._add_data, help_text="Add an item to the list.")
        self.register_interactive_command("list", self._list_data, help_text="List items in the list.")
        self.register_interactive_command("greet", self._greet, help_text="Greet the user.")

    def run(self, args: argparse.Namespace) -> int:
        self.console.print(f"Hello, [bold blue]{args.name}[/bold blue]! (Initial run)")
        return 0

    def _add_data(self, args: str) -> None:
        self._data.append(args)
        self.console.print(f"[green]Added:[/green] {args}")

    def _list_data(self, args: str) -> None:
        if self._data:
            self.console.print("[bold]Data:[/bold]")
            for item in self._data:
                self.console.print(f"- {item}")
        else:
            self.console.print("[yellow]No data yet.[/yellow]")

    def _greet(self, args: str) -> None:
        """Greets a user by name.  Example: greet Alice"""
        if args:
            self.console.print(f"Hello, [bold cyan]{args}[/bold cyan]! (Interactive greet)")
        else:
            self.console.print("Please provide a name to greet (e.g., 'greet Alice').")


if __name__ == "__main__":
    app = MyInteractiveCLI()
    exit_code = app.main()
    raise SystemExit(exit_code)
