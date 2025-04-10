from typing import List, Optional

import requests
import typer
from rich import print as rprint  # Use rich print for better formatting
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

BASE_URL = "http://localhost:8000/tasks"

app = typer.Typer(
    help="CLI for managing Tasks via the docy API.",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)
console = Console()


def _handle_api_error(response: requests.Response):
    """Handles common API errors and prints user-friendly messages."""
    if response.status_code == 404:
        detail = response.json().get("detail", "Resource not found.")
        rprint(f"[bold red]Error:[/bold red] {detail} (Status: 404)")
    elif response.status_code == 400:
        detail = response.json().get("detail", "Bad request.")
        rprint(f"[bold red]Error:[/bold red] {detail} (Status: 400)")
    elif response.status_code == 409:
        detail = response.json().get("detail", "Conflict.")
        rprint(f"[bold yellow]Warning:[/bold yellow] {detail} (Status: 409)")
    elif response.status_code >= 500:
        detail = response.json().get("detail", "Internal server error.")
        rprint(f"[bold red]Error:[/bold red] Server error: {detail} (Status: {response.status_code})")
    else:
        # Catch-all for other client-side errors if needed
        try:
            detail = response.json().get("detail", "An unexpected error occurred.")
            rprint(f"[bold red]Error:[/bold red] {detail} (Status: {response.status_code})")
        except requests.exceptions.JSONDecodeError:
            rprint(f"[bold red]Error:[/bold red] Received non-JSON response (Status: {response.status_code})")
            rprint(response.text)  # Print raw text for debugging


def _print_task_details(task: dict):
    """Prints task details in a formatted panel."""
    panel_content = f"""\
[bold cyan]ID:[/bold cyan] {task.get("id")}
[bold cyan]Title:[/bold cyan] {task.get("title")}
[bold cyan]Project ID:[/bold cyan] {task.get("project_id")}
[bold cyan]Agent ID:[/bold cyan] {task.get("agent_id") or "N/A"}
[bold cyan]Status:[/bold cyan] {task.get("status")}
[bold cyan]Priority:[/bold cyan] {task.get("priority")}
[bold cyan]Required Agent Type:[/bold cyan] {task.get("required_agent_type") or "Any"}
[bold cyan]Description:[/bold cyan]
{task.get("description") or "No description."}
"""
    rprint(Panel(panel_content, title=f"Task Details (ID: {task.get('id')})", border_style="blue"))


def _print_task_table(tasks: List[dict]):
    """Prints a list of tasks in a table."""
    if not tasks:
        rprint("[yellow]No tasks found.[/yellow]")
        return

    table = Table(title="Tasks", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=6)
    table.add_column("Name")
    table.add_column("Project ID", style="blue")
    table.add_column("Agent ID", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Priority", style="red")

    for task in tasks:
        table.add_row(
            str(task.get("id")),
            task.get("name"),
            str(task.get("project_id")),
            str(task.get("agent_id")) if task.get("agent_id") else "[dim]N/A[/dim]",
            task.get("status", "N/A"),
            str(task.get("priority", "N/A")),
        )
    console.print(table)


# --- CLI Commands ---


@app.command()
def create(
    title: str = typer.Argument(..., help="The title of the task."),
    project_id: int = typer.Argument(..., help="The ID of the project this task belongs to."),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="Optional description for the task."),
    priority: Optional[int] = typer.Option(None, "--priority", "-p", help="Optional priority level."),
    status: Optional[str] = typer.Option("PENDING", "--status", "-s", help="Initial status of the task."),
    required_agent_type: Optional[str] = typer.Option(
        None, "--agent-type", "-at", help="Required type of agent for this task."
    ),
):
    """
    Creates a new task.
    """
    task_data = {
        "title": title,
        "project_id": project_id,
        "description": description,
        "priority": priority,
        "status": status,
        "required_agent_type": required_agent_type,
    }
    # Filter out None values Optional fields not provided
    payload = {k: v for k, v in task_data.items() if v is not None}

    try:
        rprint(f"Attempting to create task for project {project_id}...")
        response = requests.post(f"{BASE_URL}/", json=payload)

        if response.status_code == status.HTTP_201_CREATED:
            task_id = response.json()  # API returns just the ID on success
            rprint(f"[bold green]Success![/bold green] Task created with ID: {task_id}")
            # Optionally fetch and display the created task
            get(task_id)
        else:
            _handle_api_error(response)
            raise typer.Exit(code=1)

    except requests.exceptions.RequestException as e:
        rprint(f"[bold red]Error:[/bold red] Could not connect to API: {e}")
        raise typer.Exit(code=1) from e


@app.command()
def get(task_id: int = typer.Argument(..., help="The ID of the task to retrieve.")):
    """
    Retrieves and displays details for a specific task.
    """
    try:
        rprint(f"Fetching task with ID: {task_id}...")
        response = requests.get(f"{BASE_URL}/{task_id}")

        if response.status_code == status.HTTP_200_OK:
            task_data = response.json()
            _print_task_details(task_data)
        else:
            _handle_api_error(response)
            raise typer.Exit(code=1)

    except requests.exceptions.RequestException as e:
        rprint(f"[bold red]Error:[/bold red] Could not connect to API: {e}")
        raise typer.Exit(code=1) from e


@app.command(name="list")  # Use 'list' as command name instead of function name
def list_tasks(
    project_id: Optional[int] = typer.Option(None, "--project-id", "-p", help="Filter tasks by Project ID."),
    agent_id: Optional[int] = typer.Option(None, "--agent-id", "-a", help="Filter tasks by assigned Agent ID."),
    unassigned: bool = typer.Option(
        False, "--unassigned", "-u", help="List only unassigned tasks (overrides --agent-id)."
    ),
):
    """
    Lists tasks, with optional filters.
    """
    params = {}
    url = BASE_URL + "/"

    if unassigned:
        url = f"{BASE_URL}"
        if project_id is not None:
            params["project_id"] = project_id
        if agent_id is not None:
            rprint("[yellow]Warning:[/yellow] --agent-id is ignored when --unassigned is used.")
    else:
        if project_id is not None:
            params["project_id"] = project_id
        if agent_id is not None:
            params["agent_id"] = agent_id

    filter_desc = "all"
    if unassigned:
        filter_desc = "unassigned"
    elif params:
        filter_desc = f"matching filters ({', '.join(f'{k}={v}' for k, v in params.items())})"

    try:
        rprint(f"Fetching {filter_desc} tasks...")
        response = requests.get(url, params=params)

        if response.status_code == status.HTTP_200_OK:
            tasks_data = response.json()
            _print_task_table(tasks_data)
        else:
            _handle_api_error(response)
            raise typer.Exit(code=1)

    except requests.exceptions.RequestException as e:
        rprint(f"[bold red]Error:[/bold red] Could not connect to API: {e}")
        raise typer.Exit(code=1) from e


@app.command()
def interactive():
    """
    Starts an interactive session to manage tasks.
    """
    rprint("[bold cyan]Welcome to Interactive Task Management![/bold cyan]")
    rprint("Type 'help' for available commands, 'exit' to quit.")

    while True:
        command_str = typer.prompt("\nTask >", default="").strip()
        if not command_str:
            continue
        if command_str.lower() == "exit":
            break
        elif command_str.lower() == "help":
            rprint("\nAvailable commands:")
            rprint("  [bold]create[/bold]  - Create a new task (prompts for details)")
            rprint("  [bold]get[/bold]     - Get details for a specific task (prompts for ID)")
            rprint("  [bold]list[/bold]    - List tasks (prompts for filters)")
            rprint("  [bold]unassigned[/bold] - List unassigned tasks (prompts for project filter)")
            rprint("  [bold]help[/bold]    - Show this help message")
            rprint("  [bold]exit[/bold]    - Exit the interactive session")
            continue

        parts = command_str.split(maxsplit=1)
        command = parts[0].lower()
        args_str = parts[1] if len(parts) > 1 else ""

        try:  # Wrap command execution to prevent crashing the interactive loop
            if command == "create":
                rprint("--- Create New Task ---")
                title = typer.prompt("Title")
                project_id_str = typer.prompt("Project ID")
                try:
                    project_id = int(project_id_str)
                except ValueError:
                    rprint("[bold red]Error:[/bold red] Project ID must be an integer.")
                    continue
                description = typer.prompt("Description (optional)", default="") or None
                priority_str = typer.prompt("Priority (optional, integer)", default="")
                priority = int(priority_str) if priority_str.isdigit() else None
                status = typer.prompt("Status", default="PENDING") or "PENDING"
                required_agent_type = typer.prompt("Required Agent Type (optional)", default="") or None

                create(
                    title=title,
                    project_id=project_id,
                    description=description,
                    priority=priority,
                    status=status,
                    required_agent_type=required_agent_type,
                )

            elif command == "get":
                task_id_str = typer.prompt("Task ID to get")
                try:
                    task_id = int(task_id_str)
                    get(task_id=task_id)
                except ValueError:
                    rprint("[bold red]Error:[/bold red] Task ID must be an integer.")
                    continue

            elif command == "list":
                project_id_str = typer.prompt("Filter by Project ID (optional, integer)", default="")
                agent_id_str = typer.prompt("Filter by Agent ID (optional, integer)", default="")
                project_id = int(project_id_str) if project_id_str.isdigit() else None
                agent_id = int(agent_id_str) if agent_id_str.isdigit() else None
                list_tasks(project_id=project_id, agent_id=agent_id)

            elif command == "unassigned":
                project_id_str = typer.prompt("Filter by Project ID (optional, integer)", default="")
                project_id = int(project_id_str) if project_id_str.isdigit() else None
                list_tasks(project_id=project_id, unassigned=True)

            else:
                rprint(f"[yellow]Unknown command:[/yellow] '{command}'. Type 'help' for options.")

        except typer.Exit:
            # Prevent typer.Exit from stopping the interactive loop, but signal failure
            rprint("[yellow]Command execution failed.[/yellow]")
        except Exception as e:
            # Catch other unexpected errors during command processing
            rprint(f"[bold red]An unexpected error occurred:[/bold red] {e}")


if __name__ == "__main__":
    from fastapi import status

    app()
