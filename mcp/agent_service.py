import asyncio
from typing import Dict, List, Any, Optional
import time

from mcp import ClientSession
from mcp.client.sse import sse_client

from action import execute_tool
from decision import generate_plan
from memory import MemoryItem, MemoryManager
from perception import extract_perception

class AgentService:
    def __init__(self):
        self.memory = MemoryManager()
        self.max_steps = 10
        self.host = "127.0.0.1"
        self.port = 7172
        self.initialized = False
        
    async def initialize(self):
        """Initialize the agent service if not already initialized"""
        if self.initialized:
            return
            
        # Store basic user context
        self.memory.store(MemoryItem(text="Agent initialized via Chrome extension"))
        self.initialized = True
    
    async def process_query(self, query: str) -> str:
        """Process a user query and return the result"""
        await self.initialize()
        
        try:
            host_port = f"http://{self.host}:{self.port}/sse"
            print(f'[agent_service] connecting with server at {host_port}')
            
            async with sse_client(host_port) as (read, write):
                print("[agent_service] connected with server")
                return await self._execute_query(read, write, query)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error processing query: {str(e)}"
    
    async def _execute_query(self, read, write, query: str) -> str:
        """Execute a query using the MCP session"""
        async with ClientSession(read, write) as session:
            print("[agent_service] Session created, initializing...")
            
            await session.initialize()
            print("[agent_service] MCP session initialized")
            
            # Get available tools
            tools_result = await session.list_tools()
            print("Available tools:", [t.name for t in tools_result.tools])
            tools = tools_result.tools
            
            # Format tool descriptions
            tools_description = []
            for i, tool in enumerate(tools):
                try:
                    params = tool.inputSchema
                    desc = getattr(tool, 'description', 'No description available')
                    name = getattr(tool, 'name', f'tool_{i}')
                    
                    if 'properties' in params:
                        param_details = [
                            self._format_param(param_name, param_info, params)
                            for param_name, param_info in params['properties'].items()
                        ]
                        params_str = ', '.join(param_details)
                    else:
                        params_str = 'no parameters'

                    tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                    tools_description.append(tool_desc)
                except Exception as e:
                    print(f"[agent_service] Error processing tool {i}: {e}")
                    tools_description.append(f"{i+1}. Error processing tool")
            
            tools_description = "\n".join(tools_description)
            print(f"[agent_service] {len(tools)} tools loaded")
            
            # Process the query
            user_input = query
            original_query = query
            step = 0
            final_result = ""
            
            while step < self.max_steps:
                print(f"[agent_service] Step {step + 1} started...")
                
                perception = await extract_perception(user_input)
                print(f"[agent_service] Objective: {perception.objective}, Tool hint: {perception.tool_hint}")
                
                retrieved = await self.memory.recall(query=user_input)
                print(f"[agent_service] Retrieved {len(retrieved)} relevant memories")
                
                plan = await generate_plan(perception, retrieved, tool_descriptions=tools_description)
                print(f"[agent_service] Plan generated: {plan}")
                
                if plan.startswith("FINAL_ANSWER:"):
                    final_result = plan.replace("FINAL_ANSWER:", "").strip()
                    print(f"[agent_service] ✅ FINAL RESULT: {final_result}")
                    break
                
                try:
                    result = await execute_tool(session, tools, plan)
                    print(f"[agent_service] {result.tool_name} returned: {result.result}")
                    
                    self.memory.store(MemoryItem(
                        text=f"Tool call: {result.tool_name} with {result.arguments}, got: {result.result}"
                    ))
                    
                    user_input = f"Original task: {original_query}\nPrevious output: {result.result}\nWhat should I do next?"
                    
                except Exception as e:
                    print(f"[agent_service] Tool execution failed: {e}")
                    return f"Tool execution error: {str(e)}"
                
                step += 1
                
                # If we've reached max steps without a final answer
                if step == self.max_steps:
                    final_result = f"Reached maximum number of steps ({self.max_steps}) without a final answer. Last result: {result.result if 'result' in locals() else 'No result'}"
            
            return final_result or "Processing complete, but no final answer was produced."
    
    def _format_param(self, name, schema, root_schema):
        """Format a parameter description"""
        if '$ref' in schema:
            ref_schema = self._resolve_ref(schema['$ref'], root_schema)
            inner_props = ref_schema.get('properties', {})
            inner_details = []
            for inner_name, inner_info in inner_props.items():
                inner_type = inner_info.get('type', 'unknown')
                inner_details.append(f"{inner_name}:{inner_type}")
            return f"{name}: {ref_schema.get('title', name)}({', '.join(inner_details)})"
        else:
            param_type = schema.get('type', 'unknown')
            return f"{name}: {param_type}"
    
    def _resolve_ref(self, ref, schema):
        """Resolve a $ref in a JSON schema."""
        parts = ref.strip('#/').split('/')
        resolved = schema
        for part in parts:
            resolved = resolved.get(part, {})
        return resolved

# Create a singleton instance
agent_service = AgentService() 