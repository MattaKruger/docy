from argparse import Namespace

from base import Base


class AgentCLI(Base):
    def __init__(self):
        super().__init__(description="Agent CLI app")

    def add_arguments(self) -> None:
        self._parser.add_argument("-n", "--name", help="Agent name", default="default")

    def run(self, args: Namespace) -> int:
        self.console.print(f"Hello, [bold blue]{args.name}[/bold blue]")
        return 0


if __name__ == "__main__":
    app = AgentCLI()
    exit_code = app.main()
    raise SystemExit(exit_code)
