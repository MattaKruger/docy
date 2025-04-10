import logfire
from mcp.server.fastmcp import FastMCP
from tools import file_system, task, web

logfire.configure()

server = FastMCP("PydanticAI structured server")

all_tools = {}
all_tools.update(task.exported_tools)
all_tools.update(file_system.exported_tools)
all_tools.update(web.exported_tools)


# Register tools
for name, func in all_tools.items():
    if func:
        server.tool(name=name)(func)
    else:
        logfire.warning(f"Tool '{name}' is defined but not implemented, skipping registration.")


def main():
    logfire.info("Starting FastMCP server...")
    server.run()


if __name__ == "__main__":
    main()
