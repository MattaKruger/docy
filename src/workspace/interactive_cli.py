from typing import Dict, Optional, List

import typer

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style

from pydantic import BaseModel, Field

import shlex
import sys
import click

import rich

from rich.panel import Panel


class Settings(BaseModel):
    theme: str = Field(default="default")

class Process(BaseModel):
    agent: Optional[Dict[str, str]] = Field(default_factory=dict)
    task: Optional[Dict[str, str]] = Field(default_factory=dict)

class State(BaseModel):
    processes: List[Process] = Field(default_factory=list)
    last_result: Optional[str] = Field(default=None)
    files_processed: int = Field(default=0)

class AppState(BaseModel):
    state: State = Field(default_factory=State)
    settings: Settings = Field(default_factory=Settings)


app_state = AppState()

app = typer.Typer(
    name="my-interactive-cli",
    help="A sample interactive CLI combining Typer and prompt_toolkit.",
    add_completion=False
)

def themed_print(message: str, theme: str = "bold magenta"):
    rich.print(f"[{theme}]{message}[/]", end="\n")

@app.command()
def hello(
    name: str = typer.Argument(..., help="The name to say hello to."),
    formal: bool = typer.Option(False, "--formal", "-f", help="Use a formal greeting."),
):
    """
    Greets the user.
    """
    greeting = "Greetings" if formal else "Hello"
    message = f"{greeting}, {name}!"

    themed_print(message, theme="bold magenta")

    app_state.state.last_result = message

@app.command()
def process_file(
    filename: str = typer.Argument(..., help="File to process (simulated).")
):
    """
    Simulates processing a file and updates state. Uses Rich Panel.
    """
    rich.print(Panel(
        f"Simulating processing for file: '[bold green]{filename}[/]'\nStatus: [yellow]Completed[/]",
        title="[blue]File Processing[/]",
        border_style="blue",
        expand=False
    ))
    app_state.state.files_processed += 1
    app_state.state.last_result = f"Processed {filename}"

@app.command()
def get_tasks(

):
    """Fetches all the tasks for a given project."""
    pass

@app.command()
def select_agent(
    name: str = typer.Argument(..., help="Name of the agent to select")
):
    """Select an agent to use for this session"""
    app_state.state.selected_agent = name
    app_state.state.last_result = f"Selected agent: {name}"


@app.command()
def select_task(
    index: int = typer.Argument(..., help="Select index of task to handle")
):
    """Select a task to handle"""
    app_state.state.selected_task = index
    app_state.state.last_result = f"Selected task: {index}"


@app.command()
def goodbye(
    name: str,
    show_last: bool = typer.Option(False, "--show-last", help="Show the last result."),
):
    """
    Says goodbye to the user.
    """
    message = f"Goodbye, {name}!"
    themed_print(message)
    if show_last and app_state.state.last_result:
        themed_print(f"Last result was: {app_state.state.last_result}", theme="bold magenta")
    app_state.state.last_result = message

@app.command()
def show_state():
    """
    Displays the current internal state.
    """

    themed_print(f"Current state: {app_state.state}")

# --- prompt_toolkit REPL Setup ---

cli_command = typer.main.get_command(app)
command_names = list(cli_command.commands.keys())

history = FileHistory('.my_interactive_cli_history')
completer = WordCompleter(command_names + ['exit', 'quit'], ignore_case=True)
style = Style.from_dict({
    'prompt': '#ansicyan bold',
    'completion-menu.completion.current': 'bg:#00aaaa #000000',
    'completion-menu.completion': 'bg:#008888 #ffffff',
    'rprompt': 'bg:#ff0066 #ffffff',
})

def run_repl():
    """Runs the interactive Read-Eval-Print Loop."""
    print("Welcome to the interactive CLI!")
    print("Type 'exit' or 'quit' to leave.")

    while True:
        try:
            user_input = prompt(
                'cli> ',
                history=history,
                completer=completer,
                auto_suggest=AutoSuggestFromHistory(),
                style=style,
                rprompt=lambda: f"Last: {str(app_state.state.last_result)[:20]}" if app_state.state.last_result else ""
            )

            input_lower = user_input.strip().lower()
            if input_lower in ['exit', 'quit']:
                print("Exiting.")
                break

            if not user_input.strip():
                continue

            try:
                args = shlex.split(user_input)
            except ValueError as e:
                print(f"Error parsing input: {e}")
                continue

            try:
                app(args=args, prog_name="cli", standalone_mode=False)
            except click.exceptions.MissingParameter as e:
                print(f"Error: Missing argument '{e.param_hint}' for command '{e.ctx.command.name}'.")
                print(e.format_message())
            except click.exceptions.BadParameter as e:
                print(f"Error: Invalid value for {e.param_hint}: {e.format_message()}")
            except click.exceptions.UsageError as e:
                print(f"Usage Error: {e.format_message()}")
            except click.exceptions.Abort:
                print("Command aborted.")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                import traceback
                traceback.print_exc()

        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

# --- Entry Point ---

@app.callback()
def main_callback(ctx: typer.Context):
    """
    Main callback, useful for global options or setup if needed
    when running non-interactively.
    """
    pass

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        run_repl()
    else:
        app()
