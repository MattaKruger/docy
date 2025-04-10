from rich.console import Console
from rich.prompt import Prompt


class Main:
    def __init__(self) -> None:
        self.console = Console()
        self.active_consoles = []

    def print(self, message):
        self.console.print(message)

    def prompt(self, question):
        return Prompt.ask(question)

    def process_prompt(self):
        pass

    def add_console(self):
        self.active_consoles.append(Console())


class CodeWriter:
    def __init__(self) -> None:
        pass

    def process_prompt(self):
        pass


class NoteWriter:
    def __init__(self) -> None:
        pass

    def process_prompt(self):
        pass


cli = Main()
answer = cli.prompt("What do you want to do?")

cli.print(answer)
