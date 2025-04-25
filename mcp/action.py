
import json
from typing import Any, Dict, Union

from mcp import ClientSession
from pydantic import BaseModel


try:
    from agent import log
except ImportError:
    import datetime
    def log(stage: str, msg: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] [{stage}] {msg}")


class ToolCallResult(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result: Union[str, list, dict]
    raw_response: Any
    

def parse_function_call(response_text: str) -> tuple[str, Dict[str, Any]]:
    if not response_text.startswith("FUNCTION_CALL:"):
            raise ValueError("Not a valid FUNCTION_CALL")
    try:
        _, function_info = response_text.split(":", 1)
        try:
            function_info_json = json.loads(function_info)
            func_name = function_info_json.get("func_name")
            params = function_info_json.get("param", {})
            
            print(f"DEBUG: func_name: {func_name}")
            print(f"DEBUG: params: {params}")
            
            return func_name, params

        except Exception as e:
            print(f"DEBUG: Error details: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            import traceback
            traceback.print_exc()
    except Exception as e:
        log("parser", f"❌ Failed to parse FUNCTION_CALL: {e}")
        raise

async def execute_tool(session: ClientSession, tools: list[Any], response: str) -> ToolCallResult:
    """Executes a FUNCTION_CALL via MCP tool session."""
    try:
        tool_name, arguments = parse_function_call(response)

        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found in registered tools")

        log("tool", f"⚙️ Calling '{tool_name}' with: {arguments}")
        result = await session.call_tool(tool_name, arguments=arguments)

        if hasattr(result, 'content'):
            if isinstance(result.content, list):
                out = [getattr(item, 'text', str(item)) for item in result.content]
            else:
                out = getattr(result.content, 'text', str(result.content))
        else:
            out = str(result)

        log("tool", f"✅ {tool_name} result: {out}")
        return ToolCallResult(
            tool_name=tool_name,
            arguments=arguments,
            result=out,
            raw_response=result
        )

    except Exception as e:
        log("tool", f"⚠️ Execution failed for '{response}': {e}")
        raise


if __name__ == "__main__":
    from pdb import set_trace
    resp = """FUNCTION_CALL: {"func_name":"add_list","param":{"input":{"l":[2,3,5,7,11]}}}"""
    f_name, params = parse_function_call(resp)
    set_trace()
    print(params)