from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import logfire
from httpx import AsyncClient
from pydantic import BaseModel, Field
from pydantic_ai import RunContext
from pydantic_ai.agent import Agent

# from .github_service import GithubService

# from models import ProjectMetadata, Project, ProjectType
# from schemas import ProjectMetadataIn


# class ProjectService:
#     def __init__(self, project_repository: ProjectRepository):
#         self.project_repo = project_repository
#         self.github_service = GithubService()
#         self.project_creator = project_agent
#         self.example_generator = example_generator

#     async def _generate_example_files(self, project: Project):
#         pass

#     async def _get_project_docs(self, doc_path: str):
#         pass

#     async def _generate_developer_spec(self,):
#         pass

#     async def create_python_project(
#         self,
#         name: str,
#         description: str,
#         project_type: ProjectType,
#         frameworks: List[str],
#         languages=["Python"],
#     ):
#         project_metadata = ProjectMetadata(frameworks=frameworks, languages=languages)
#         project = Project(
#             name=name, description=description, project_type=project_type, project_metadata=project_metadata
#         )
#         project_db = await self.project_repo.create_project_with_metadata(project)
#         if not project_db:
#             return None

#         example_files = self._generate_example_files(project_db)

#         # find_docs = self.get_docs(create_metadata.frameworks, create_metadata.languages)
#         # create_metadata.docs.update(find_docs)

#         # self.project_repo.create_project(create_metadata)


# class LLMCodegenWorkflow:
#     def __init__(self, project_name, model="gpt-4o"):
#         self.project_name = project_name
#         self.model = model
#         self.agent = project_agent

#         self.spec = None
#         self.prompt_plan = None
#         self.todo_list = None
#         self.output_dir = f"projects/{project_name}"
#         self.conversation_history: Dict[str, Any]

#     # Step 1: Idea Honing Methods
#     def brainstorm_idea(self, idea_description: str):
#         """Start the iterative brainstorming process with an initial idea description"""

#         prompt = f"""
#         Ask me one question at a time so we can develop a thorough, step-by-step spec for this idea. Each question should build on my previous answers, and our end goal is to have a detailed specification I can hand off to a developer. Let’s do this iteratively and dig into every relevant detail. Remember, only one question at a time.

#         Here’s the idea:
#         {idea_description}
#         """
#         agent_deps = AgentDeps(http_client=None)

#         brainstorm_result = project_agent.run(prompt, deps=agent_deps)


#     async def generate_spec(self):
#         """Generate a comprehensive spec from the brainstorming conversation"""
#         # Maybe overwrite .system_prompt, not sure yet.
#         prompt = f"""
#         Now that we’ve wrapped up the brainstorming process, can you compile our findings into a comprehensive, developer-ready specification? Include all relevant requirements, architecture choices, data handling details, error handling strategies, and a testing plan so a developer can immediately begin implementation.
#         {self.conversation_history}
#         """
#         response = await project_agent.run(
#             prompt,
#             message_history=self.conversation_history, # TODO: fix type
#         )
#         print(f"Usage: {response.usage()}")
#         developer_spec = response.data
#         return developer_spec

#     def save_spec(self):
#         """Save the generated spec to spec.md"""


#     # Step 2: Planning Methods
#     def generate_tdd_plan(self, spec):
#         """Generate a test-driven development plan with iterative steps"""
#         pass

#     def generate_non_tdd_plan(self, spec):
#         """Generate a standard development plan with iterative steps"""
#         pass

#     def generate_todo_list(self, prompt_plan):
#         """Generate a todo list from the prompt plan"""
#         pass

#     def save_planning_artifacts(self):
#         """Save the prompt plan and todo list"""
#         pass

#     # Step 3: Execution Methods
#     def setup_project_boilerplate(self, tech_stack):
#         """Set up initial project structure and boilerplate"""
#         pass

#     def execute_prompt_step(self, step_number):
#         """Execute a specific step from the prompt plan"""
#         pass

#     def run_tests_for_step(self, step_number):
#         """Run tests for the current implementation step"""
#         pass

#     def update_todo_status(self, step_number, status):
#         """Update the status of a todo item"""
#         pass

#     # Non-greenfield Methods
#     def analyze_existing_codebase(self, repo_path, ignore_patterns=None):
#         """Generate context from an existing codebase"""
#         pass

#     def generate_code_review(self, code_context):
#         """Generate a code review from the codebase context"""
#         pass

#     def generate_github_issues(self, code_context):
#         """Generate GitHub issues from the codebase context"""
#         pass

#     def generate_missing_tests(self, code_context):
#         """Identify missing tests in the codebase"""
#         pass

#     def generate_readme(self, code_context):
#         """Generate a README.md from the codebase context"""
#         pass

#     # Utility Methods
#     def export_to_aider(self, step_number=None):
#         """Export current context to aider for interactive implementation"""
#         pass

#     def export_to_claude(self, step_number=None):
#         """Export current context to Claude for interactive implementation"""
#         pass

#     def check_progress(self):
#         """Check overall project progress based on todo list"""
#         pass

#     def load_prompt_templates(self):
#         """Load prompt templates for various tasks"""
#         pass


@dataclass
class AgentDeps:
    http_client: AsyncClient | None


@dataclass
class BrainstormContext:
    idea_description: str
    previous_answers: List[str]

    def __post__init__(self):
        if self.previous_answers is None:
            self.previous_answers = list()


class SpecResult(BaseModel):
    final_specification: str | None = Field(default=None)


brainstorm_agent = Agent(
    "groq:llama-3.3-70b-versatile",
    deps_type=BrainstormContext,
    result_type=SpecResult,
    system_prompt="""
    You are a specialized brainstorming assistant that helps users develop detailed specifications.

    Your approach:
    1. Ask ONE question at a time - never multiple questions in one response
    2. Each question should logically build on previous answers
    3. Ask specific, focused questions to extract clear requirements
    4. Your goal is to transform a vague idea into a comprehensive specification
    5. Cover functional requirements, user experience, technical considerations, edge cases, etc.
    6. When you have gathered enough information, summarize everything into a final specification

    Remember: Only ask ONE question per interaction. Build knowledge iteratively.
    """,
)

# @brainstorm_agent.tool
# def check_specification_complete(ctx: RunContext[BrainstormContext]) -> bool:
#     """
#     Determine if we have enough information to create a final specification.
#     Return True if specification is complete, False if more questions needed.
#     """
#     return len(ctx.deps.previous_answers) >= 10


def run_brainstorm_loop(idea_description: str):
    """Run the brainstorm loop with a user until a complete spec is created."""
    context = BrainstormContext(idea_description=idea_description, previous_answers=[])

    print("Starting brainstorm session for your idea...")
    print(f"Initial idea: {idea_description}\n")

    while True:
        result = brainstorm_agent.run_sync(
            "Based on what we've discussed so far, ask me your next question to develop this spec further.",
            deps=context,
        )
        question = result.data
        print(f"\nAgent: {question}")

        if "final_description" in result.data.model_dump():
            print("\n== FINAL SPECIFICATION ===\n")
            print(result.data.final_specification)
            break

        user_answer = input("\nYour answer: ")
        context.previous_answers.append(f"Q: {question}\nA: {user_answer}")

        print(f"[Progress: {len(context.previous_answers)} questions answered]")


if __name__ == "__main__":
    idea = input("Describe your idea:")
    run_brainstorm_loop(idea)
