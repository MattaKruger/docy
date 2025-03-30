import asyncio
from typing import Any, Callable, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.usage import Usage
from rich.console import Console, ConsoleOptions, RenderResult
from rich.live import Live
from rich.markdown import CodeBlock, Markdown
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.text import Text

from system_prompts import (
    context_prompt,
    data_modelling_prompt,
    erd_generator_prompt,
    implementation_prompt,
    project_brainstorming_prompt,
)


# Define your models
class DataModelDetails(BaseModel):
    name: str = Field(..., description="The name of the data model.")
    description: str = Field(..., description="A brief description of the data model.")
    fields: list[str] = Field(..., description="A list of field names for the data model.")
    primary_key: str = Field(..., description="The primary key field for the data model.")
    foreign_keys: list[str] = Field(..., description="A list of foreign key fields for the data model.")


class Project(BaseModel):
    project_name: str = Field(..., description="The name of the project.")
    project_description: str = Field(..., description="A brief description of the project.")


# Initialize the model
groq_model = GroqModel("deepseek-r1-distill-qwen-32b")

# Define your agents
project_brainstorming_agent = Agent(
    groq_model,
    system_prompt=project_brainstorming_prompt,
)
data_modelling_agent = Agent(groq_model, system_prompt=data_modelling_prompt)
erd_generator_agent = Agent(groq_model, system_prompt=erd_generator_prompt)
code_generator_agent = Agent(groq_model, system_prompt=implementation_prompt)
context_agent = Agent(groq_model, system_prompt=context_prompt)
chat_agent = Agent(groq_model, system_prompt="You are a helpful assistant.")


# Type for agent functions
AgentFn = Callable[[Dict[str, str]], str]


class AgentCLI:
    """A reusable CLI interface for interacting with agents."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.usage = Usage()
        self._setup_prettier_code_blocks()

    def _setup_prettier_code_blocks(self):
        """Make rich code blocks prettier and easier to copy."""

        class SimpleCodeBlock(CodeBlock):
            def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
                code = str(self.text).rstrip()
                yield Text(self.lexer_name, style="dim")
                yield Syntax(
                    code,
                    self.lexer_name,
                    theme=self.theme,
                    background_color="default",
                    word_wrap=True,
                )
                yield Text(f"/{self.lexer_name}", style="dim")

        Markdown.elements["fence"] = SimpleCodeBlock

    async def run_agent(
        self,
        agent: Agent,
        inputs: Dict[str, str],
        prompt_template: str,
        title: str,
        description: str = "",
        save_default_filename: str = "output.md",
    ) -> str:
        """Run an agent with the given inputs and return the result."""
        self.console.rule(f"[bold blue]{title}[/bold blue]")

        if description:
            self.console.print(description, style="italic")

        # Log inputs
        for key, value in inputs.items():
            self.console.log(f"{key}: {value}", style="dim")

        # Prepare prompt by formatting template with inputs
        formatted_prompt = prompt_template.format(**inputs)

        # Accumulated response for saving to file later
        accumulated_response = ""

        with Live(Markdown(""), console=self.console, vertical_overflow="visible") as live:
            async with agent.run_stream(formatted_prompt) as response:
                async for chunk in response.stream_text(delta=True):
                    accumulated_response += chunk
                    live.update(Markdown(accumulated_response))

        self.console.log(f"{title} complete! ✨", style="green bold")

        # Log usage statistics if available
        try:
            usage_info = response.usage()
            self.console.log("Usage statistics:", style="blue")
            self.console.print(usage_info)
        except (AttributeError, TypeError):
            self.console.log("Usage statistics not available", style="yellow")

        # Offer to save the result
        self.console.print("\nWould you like to save this output?", style="yellow")
        save_option = Prompt.ask("Save to file? (y/n)", default="y")

        if save_option.lower() == "y":
            filename = Prompt.ask("Enter filename", default=save_default_filename)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(accumulated_response)
            self.console.print(f"Saved to {filename}", style="green")

        return accumulated_response

    async def get_inputs(self, input_fields: Dict[str, Tuple[str, str]]) -> Dict[str, str]:
        """Get inputs from the user for the agent.

        Args:
            input_fields: Dictionary mapping field names to (prompt, default) tuples

        Returns:
            Dictionary of input values keyed by field name
        """
        inputs = {}
        for field_name, (prompt_text, default) in input_fields.items():
            value = Prompt.ask(prompt_text, default=default)
            inputs[field_name] = value
        return inputs

    async def run_workflow(self, workflow_name: str, steps: List[Dict[str, Any]]):
        """Run a multi-step workflow with multiple agents.

        Args:
            workflow_name: Name of the workflow
            steps: List of step configurations, each containing:
                - agent: The Agent to use
                - title: Step title
                - description: Step description
                - input_fields: Dict of input fields
                - prompt_template: Template for the prompt
                - save_default_filename: Default filename for saving
        """
        self.console.rule(f"[bold magenta]{workflow_name} Workflow[/bold magenta]")

        results = {}

        for i, step in enumerate(steps):
            self.console.print(f"\n[Step {i + 1}/{len(steps)}] {step['title']}", style="bold cyan")

            # Get inputs by combining previous results with new user inputs
            context_inputs = {}
            if "context_from_previous" in step:
                for dest_key, source_info in step["context_from_previous"].items():
                    step_name, result_key = source_info
                    if step_name in results and result_key in results[step_name]:
                        context_inputs[dest_key] = results[step_name][result_key]

            # Get any additional inputs needed from the user
            user_inputs = await self.get_inputs(step.get("input_fields", {}))

            # Combine all inputs
            all_inputs = {**context_inputs, **user_inputs}

            # Run the agent
            result = await self.run_agent(
                agent=step["agent"],
                inputs=all_inputs,
                prompt_template=step["prompt_template"],
                title=step["title"],
                description=step.get("description", ""),
                save_default_filename=step.get(
                    "save_default_filename", f"{step['title'].lower().replace(' ', '_')}.md"
                ),
            )

            # Store the result
            step_name = step.get("name", f"step_{i}")
            results[step_name] = {
                "output": result,
                **all_inputs,  # Also store the inputs used
            }

        self.console.rule("[bold magenta]Workflow Complete[/bold magenta]")
        return results

    def show_usage_report(self):
        """Display the total usage report."""
        self.console.rule("[bold blue]Usage Report[/bold blue]")
        self.console.print(self.usage)


class ChatInterface:
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.agents = {"chat-agent": chat_agent}
        self.conversation_history = []
        self.current_agents = []

    def list_available_agents(self):
        """Display available agents and allow selection."""
        self.console.print("\nAvailable Agents:")
        for idx, (name, agent) in enumerate(self.agents.items(), start=1):
            self.console.print(f"[{idx}] {name}: {agent.system_prompt}...")
        return [agent for agent in self.agents.values()]

    async def get_user_input(self):
        """Get user input for the chat."""
        return Prompt.ask("Enter your message (type 'help' for options)")

    async def run_chat(self):
        """Run the chat interface."""
        self.console.rule("[bold blue]AI Chat Interface[/bold blue]")
        self.console.print("Welcome to the AI Chat Interface!")
        self.console.print("You can interact with multiple agents in this chat.")
        self.console.print("Type 'help' for available commands.\n")

        while True:
            user_input = await self.get_user_input()

            if user_input.lower() == "help":
                self.display_help_menu()
                continue

            if user_input.lower() == "agents":
                self.list_available_agents()
                continue

            if user_input.lower() == "exit":
                break

            # Process the user input
            await self.process_chat(user_input)

    async def process_chat(self, user_input: str):
        """Process the user input and generate responses."""
        # Allow users to select agents dynamically
        if "agent:" in user_input:
            agent_name = user_input.split("agent:")[1].strip()
            if agent_name in self.agents:
                self.current_agents = [self.agents[agent_name]]
                self.console.print(f"Switched to agent: {agent_name}")

        # Generate response
        response = await self.generate_response(user_input)
        self.conversation_history.append((user_input, response))
        self.display_conversation(user_input, response)

    async def generate_response(self, user_input: str) -> str:
        """Generate a response using the selected agents."""
        if not self.current_agents:
            self.current_agents = list(self.agents.values())

        # Combine responses from multiple agents
        responses = []
        for agent in self.current_agents:
            response = await agent.run(user_input)
            responses.append(response.data)

        return "\n\n".join(responses)

    def display_conversation(self, user_input: str, response: str):
        """Display the conversation in a user-friendly way."""
        with Live(Markdown(""), console=self.console, vertical_overflow="visible") as live:
            markdown = Markdown(f"### Chat History\n**You**: {user_input}\n\n**AI**: {response}\n")
            live.update(markdown)

    def display_help_menu(self):
        """Display available commands."""
        self.console.print("\nAvailable Commands:")
        self.console.print("- Type your message to chat.")
        self.console.print("- `agent:<name>`: Switch to a specific agent.")
        self.console.print("- `help`: Show this menu.")
        self.console.print("- `exit`: Quit the chat.")


# Example usage of the AgentCLI
async def main():
    # cli = AgentCLI()
    chat = ChatInterface()

    await chat.run_chat()
    # # Option 1: Run a single agent
    # project_inputs = await cli.get_inputs({
    #     'project_name': ('Enter project name', 'Docy'),
    #     'project_description': ('Enter project description', 'A markdown document management system'),
    #     'project_language': ('Enter project language', 'Python')
    # })

    # await cli.run_agent(
    #     agent=project_brainstorming_agent,
    #     inputs=project_inputs,
    #     prompt_template="""
    #     Let's brainstorm about a project.
    #     project_name: {project_name}
    #     project_description: {project_description}
    #     project_language: {project_language}
    #     """,
    #     title="Project Brainstorming",
    #     save_default_filename="brainstorm.md"
    # )

    # Option 2: Or define a workflow with multiple steps
    project_workflow = [
        {
            "name": "brainstorm",
            "agent": project_brainstorming_agent,
            "title": "Project Brainstorming",
            "description": "Generating ideas for the project",
            "input_fields": {
                "project_name": ("Enter project name", "Docy"),
                "project_description": ("Enter project description", "A markdown document management system"),
                "project_language": ("Enter project language", "Python"),
            },
            "prompt_template": """
            Let's brainstorm about a project.
            project_name: {project_name}
            project_description: {project_description}
            project_language: {project_language}
            """,
            "save_default_filename": "brainstorm.md",
        },
        {
            "name": "data_modelling",
            "agent": data_modelling_agent,
            "title": "Data Modelling",
            "description": "Creating SQLModel data models for the project",
            "context_from_previous": {
                "project_name": ("brainstorm", "project_name"),
                "project_description": ("brainstorm", "project_description"),
                "brainstorming_results": ("brainstorm", "output"),
            },
            "prompt_template": """
            Based on the brainstorming results, create SQLModel data models for the project.

            Project: {project_name}
            Description: {project_description}

            Brainstorming Results:
            {brainstorming_results}

            Please create appropriate SQLModel classes for this project.
            """,
            "save_default_filename": "data_models.md",
        },
        # {
        #     'name': 'erd_generation',
        #     'agent': erd_generator_agent,
        #     'title': 'ERD Generation',
        #     'description': 'Generating an Entity Relationship Diagram for the project',
        #     'context_from_previous': {
        #         'project_name': ('data_modelling', 'project_name'),
        #         'project_description': ('data_modelling', 'project_description'),
        #         'data_models': ('data_modelling', 'output')
        #     },
        #     'prompt_template': """
        #     Based on the data models, generate an Entity Relationship Diagram for the project.
        #     Project: {project_name}
        #     Description: {project_description}
        #     Data Models:
        #     {data_models}
        #     Please create an ERD diagram for this project.
        #     """,
        #     'save_default_filename': 'erd.md'
        # },
        {
            "name": "code_generation",
            "agent": code_generator_agent,
            "title": "Code Generation",
            "description": "Generating code for the project",
            "context_from_previous": {
                "project_name": ("data_modelling", "project_name"),
                "project_description": ("data_modelling", "project_description"),
                "data_models": ("data_modelling", "output"),
            },
            "prompt_template": """
            Based on the data models generate code for the project.

            Project: {project_name}
            Description: {project_description}

            Data Models:
            {data_models}

            Please create code for this project. Do not include any uncommented text.
            """,
            "save_default_filename": "code.py",
        },
    ]

    # await cli.run_workflow("Project Development", project_workflow)

    # cli.show_usage_report()


if __name__ == "__main__":
    asyncio.run(main())
