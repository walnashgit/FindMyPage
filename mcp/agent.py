
import asyncio
import datetime
import sys
import time

from mcp import ClientSession, StdioServerParameters, stdio_client
from mcp.client.sse import sse_client

from action import execute_tool
from decision import generate_plan
from memory import MemoryItem, MemoryManager
from perception import extract_perception


def log(stage: str, msg: str):
    now = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [{stage}] {msg}")

max_steps = 20


async def main(local: bool, host: str = "127.0.0.1", port: int = 7172):
    # reset_state()  # Reset at the start of main
    print("Starting main execution...")
    try:
        # Create a single MCP server connection
        print("Establishing connection to MCP server...")
        if local:
            host_port = "http://" + host + ":" + str(port) + "/sse"
            print(f'[agent] connecting with server at {host_port}')
            async with sse_client(host_port) as (read, write):
                print("[agent] connected with server at localhost...")
                await client_main(read, write)
        else:
            server_params = StdioServerParameters(
                command="python",
                args=["mcp_server.py"]
            )
            async with stdio_client(server_params) as (read, write):
                await client_main(read, write)
            
    except Exception as e:
        print(f"[agent] Connection error: {str(e)}")
        import traceback
        traceback.print_exc()

async def client_main(read, write):
    print("Connection established, creating session...")
    try:
        async with ClientSession(read, write) as session:
            print("[agent] Session created, initializing...")

            try:
                await session.initialize()
                print("[agent] MCP session initialized")
                
                # Get available tools
                print("Requesting tool list...")
                tools_result = await session.list_tools()
                print("Available tools:", [t.name for t in tools_result.tools])
                tools = tools_result.tools
                # tool_descriptions = "\n".join(
                #     f"- {tool.name}: {getattr(tool, 'description', 'No description')}" 
                #     for tool in tools
                # )

                tools_description = []
                for i, tool in enumerate(tools):
                    try:
                        # Get tool properties
                        params = tool.inputSchema
                        desc = getattr(tool, 'description', 'No description available')
                        name = getattr(tool, 'name', f'tool_{i}')
                        
                        # Format the input schema in a more readable way
                        if 'properties' in params:
                            param_details = [
                                format_param(param_name, param_info, params)
                                for param_name, param_info in params['properties'].items()
                            ]
                            params_str = ', '.join(param_details)
                        else:
                            params_str = 'no parameters'

                        tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                        tools_description.append(tool_desc)
                        # print(f"[agent] Added description for tool: {tool_desc}")
                    except Exception as e:
                        print(f"[agent] Error processing tool {i}: {e}")
                        tools_description.append(f"{i+1}. Error processing tool")
                
                tools_description = "\n".join(tools_description)

                log("agent", f"{len(tools)} tools loaded")

                memory = MemoryManager()
                await get_user_preference(memory=memory)
                # session_id = f"session-{int(time.time())}"

                """Get user query"""
                print("\nEnter your query (or 'exit' to quit):")
                user_input = input("🧑> ")

                query = user_input  # Store original intent
                step = 0

                while step < max_steps:
                    log("\nloop", f"Step {step + 1} started...\n")

                    perception = await extract_perception(user_input)
                    log("agent", f"Objective: {perception.objective}, Tool hint: {perception.tool_hint}")

                    # retrieved = memory.retrieve(query=user_input, top_k=3, session_filter=session_id)
                    retrieved = await memory.recall(query=user_input)
                    log("agent", f"Retrieved {len(retrieved)} relevant memories")

                    plan = await generate_plan(perception, retrieved, tool_descriptions=tools_description)
                    log("agent", f"Plan generated: {plan}")

                    if plan.startswith("FINAL_ANSWER:"):
                        log("agent", f"✅ FINAL RESULT: {plan}")
                        break

                    try:
                        result = await execute_tool(session, tools, plan)
                        log("tool", f"{result.tool_name} returned: {result.result}")

                        memory.store(MemoryItem(
                            text=f"Tool call: {result.tool_name} with {result.arguments}, got: {result.result}",
                            # type="tool_output",
                            # tool_name=result.tool_name,
                            # user_query=user_input,
                            # tags=[result.tool_name],
                            # session_id=session_id
                        ))

                        user_input = f"Original task: {query}\nPrevious output: {result.result}\nWhat should I do next?"

                    except Exception as e:
                        log("error", f"Tool execution failed: {e}")
                        break

                    step += 1
            except Exception as e:
                print(f"[agent] Session initialization error: {str(e)}")
    except Exception as e:
        print(f"[agent] Session creation error: {str(e)}")

    log("agent", "Agent session complete.")

async def get_user_preference(memory: MemoryManager):
    """Get user preference"""
    print("\nTell me few facts about yourself (or 'exit' to quit):")
    user_input = input("🧑> ")
    perception = await extract_perception(user_input)
    log("agent", f"Getting user facts - Objective: {perception.objective}, Objects: {perception.objects}, Tool hint: {perception.tool_hint}")
    memory.store(MemoryItem(text=f"User's preference: {perception.objects}"))


def format_param(name, schema, root_schema):
    if '$ref' in schema:
        ref_schema = resolve_ref(schema['$ref'], root_schema)
        inner_props = ref_schema.get('properties', {})
        inner_details = []
        for inner_name, inner_info in inner_props.items():
            inner_type = inner_info.get('type', 'unknown')
            inner_details.append(f"{inner_name}:{inner_type}")
        return f"{name}: {ref_schema.get('title', name)}({', '.join(inner_details)})"
    else:
        param_type = schema.get('type', 'unknown')
        return f"{name}: {param_type}"
    
def resolve_ref(ref, schema):
    """Resolve a $ref in a JSON schema."""
    parts = ref.strip('#/').split('/')
    resolved = schema
    for part in parts:
        resolved = resolved.get(part, {})
    return resolved

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "local":
        import argparse
        sys.argv.remove("local")
        parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
        parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
        parser.add_argument('--port', type=int, default=7172, help='Port to listen on')
        args = parser.parse_args()

        asyncio.run(main(True, args.host, args.port))
    else:
        asyncio.run(main(False))