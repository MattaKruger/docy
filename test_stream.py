import asyncio
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel

# Initialize the console
console = Console()

# Initialize the model and agent
groq_model = GroqModel("deepseek-r1-distill-qwen-32b")
agent = Agent(groq_model, system_prompt="You are a helpful assistant that provides information concisely.")


async def test_streaming():
    console.print("Starting stream test...", style="bold cyan")

    prompt = "Explain the concept of streaming in API responses in 3 short paragraphs."

    # Debug the response object first
    console.print("\nDEBUG INFO:", style="bold yellow")
    async with agent.run_stream(prompt) as response:
        console.print(f"Response type: {type(response)}")
        console.print(f"Response attributes/methods: {dir(response)}")

    # Now test streaming with accumulated output
    console.print("\nACTUAL TEST:", style="bold green")
    accumulated_output = ""

    with Live(Markdown(""), console=console, vertical_overflow="visible") as live:
        async with agent.run_stream(prompt) as response:
            # Iterate through the response (assuming it's an async iterator)
            async for chunk in response:
                # Print diagnostic info about each chunk
                chunk_type = type(chunk)
                console.print(f"\nChunk type: {chunk_type}", style="dim")

                # Try different ways to get content based on the chunk type
                if isinstance(chunk, str):
                    content = chunk
                elif hasattr(chunk, "content"):
                    content = chunk.content
                elif hasattr(chunk, "text"):
                    content = chunk.text
                else:
                    content = str(chunk)

                # Add to accumulated output
                accumulated_output += content

                # Update the display
                live.update(Markdown(accumulated_output))

                # Short delay to make it easier to see what's happening
                await asyncio.sleep(0.1)

    # Display final output
    console.print("\nFINAL OUTPUT:", style="bold magenta")
    console.print(Markdown(accumulated_output))


if __name__ == "__main__":
    asyncio.run(test_streaming())
