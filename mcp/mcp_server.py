# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp.server import Server
from starlette.routing import Mount, Route
import uvicorn
from mcp import types
from PIL import Image as PILImage
import math
import sys
import time
import subprocess
from rich.console import Console
from rich.panel import Panel
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport

from data_model import (
    AddInput, AddListInput, AddListOutput, AddOutput, CreateThumbnailInput, OpenKeynoteOutput, SubtractInput, SubtractOutput,
    MultiplyInput, MultiplyOutput, DivideInput, DivideOutput,
    PowerInput, PowerOutput, SqrtInput, SqrtOutput,
    CbrtInput, CbrtOutput, FactorialInput, FactorialOutput,
    LogInput, LogOutput, RemainderInput, RemainderOutput,
    TrigInput, TrigOutput, MineInput, MineOutput,
    ShowReasoningInput, StringToAsciiInput, StringToAsciiOutput,
    ExponentialSumInput, ExponentialSumOutput,
    FibonacciInput, FibonacciOutput,
    KeynoteRectangleInput, KeynoteRectangleOutput,
    KeynoteTextInput, KeynoteTextOutput
)
# from win32api import GetSystemMetrics

console = Console()
# instantiate an MCP server client
mcp = FastMCP("Calculator", settings= {"host": "127.0.0.1", "port": 7172})

app = FastAPI()

# DEFINE TOOLS

#addition tool
@mcp.tool()
def add(input: AddInput) -> AddOutput:
    """Add two numbers"""
    print("CALLED: add(input: AddInput) -> AddOutput:")
    return AddOutput(result=(input.a + input.b))

@mcp.tool()
def add_list(input: AddListInput) -> AddListOutput:
    """Add all numbers in a list"""
    print("CALLED: add_list(input: AddListInput) -> AddListOutput:")
    return AddListOutput(result=sum(input.l))

# subtraction tool
@mcp.tool()
def subtract(input: SubtractInput) -> SubtractOutput:
    """Subtract two numbers"""
    print("CALLED: subtract(input: SubtractInput) -> SubtractOutput:")
    return SubtractOutput(result=(input.a - input.b))

# multiplication tool
@mcp.tool()
def multiply(input: MultiplyInput) -> MultiplyOutput:
    """Multiply two numbers"""
    print("CALLED: multiply(input: MultiplyInput) -> MultiplyOutput:")
    return MultiplyOutput(result=(input.a * input.b))

#  division tool
@mcp.tool() 
def divide(input: DivideInput) -> DivideOutput:
    """Divide two numbers"""
    print("CALLED: divide(input: DivideInput) -> DivideOutput:")
    return DivideOutput(result=(input.a / input.b))

# power tool
@mcp.tool()
def power(input: PowerInput) -> PowerOutput:
    """Power of two numbers"""
    print("CALLED: power(input: PowerInput) -> PowerOutput:")
    return PowerOutput(result=int(input.a ** input.b))

# square root tool
@mcp.tool()
def sqrt(input: SqrtInput) -> SqrtOutput:
    """Square root of a number"""
    print("CALLED: sqrt(input: SqrtInput) -> SqrtOutput:")
    return SqrtOutput(result=float(input.a ** 0.5))

# cube root tool
@mcp.tool()
def cbrt(input: CbrtInput) -> CbrtOutput:
    """Cube root of a number"""
    print("CALLED: cbrt(input: CbrtInput) -> CbrtOutput:")
    return CbrtOutput(result=float(input.a ** (1/3)))

# factorial tool
@mcp.tool()
def factorial(input: FactorialInput) -> FactorialOutput:
    """Factorial of a number"""
    print("CALLED: factorial(input: FactorialInput) -> FactorialOutput:")
    return FactorialOutput(result=int(math.factorial(input.a)))

# log tool
@mcp.tool()
def log(input: LogInput) -> LogOutput:
    """Log of a number"""
    print("CALLED: log(input: LogInput) -> LogOutput:")
    return LogOutput(result=float(math.log(input.a)))

# remainder tool
@mcp.tool()
def remainder(input: RemainderInput) -> RemainderOutput:
    """Remainder of two numbers division"""
    print("CALLED: remainder(input: RemainderInput) -> RemainderOutput:")
    return RemainderOutput(result=int(input.a % input.b))

# sin tool
@mcp.tool()
def sin(input: TrigInput) -> TrigOutput:
    """Sin of a number"""
    print("CALLED: sin(input: TrigInput) -> TrigOutput:")
    return TrigOutput(result=float(math.sin(input.a)))

# cos tool
@mcp.tool()
def cos(input: TrigInput) -> TrigOutput:
    """Cos of a number"""
    print("CALLED: cos(input: TrigInput) -> TrigOutput:")
    return TrigOutput(result=float(math.cos(input.a)))

# tan tool
@mcp.tool()
def tan(input: TrigInput) -> TrigOutput:
    """Tan of a number"""
    print("CALLED: tan(input: TrigInput) -> TrigOutput:")
    return TrigOutput(result=float(math.tan(input.a)))

# @mcp.tool()
# def calculate(expression: str) -> TextContent:
#     """Calculate the result of an expression"""
#     console.print("[blue]FUNCTION CALL:[/blue] calculate()")
#     console.print(f"[blue]Expression:[/blue] {expression}")
#     try:
#         result = eval(expression)
#         console.print(f"[green]Result:[/green] {result}")
#         return TextContent(
#             type="text",
#             text=str(result)
#         )
#     except Exception as e:
#         console.print(f"[red]Error:[/red] {str(e)}")
#         return TextContent(
#             type="text",
#             text=f"Error: {str(e)}"
#         )

# mine tool
@mcp.tool()
def mine(input: MineInput) -> MineOutput:
    """Special mining tool"""
    print("CALLED: mine(input: MineInput) -> MineOutput:")
    return MineOutput(result=int(input.a - input.b - input.b))

# reasoning tool
@mcp.tool()
def show_reasoning(input: ShowReasoningInput) -> TextContent:
    """Show the step-by-step reasoning process"""
    console.print("[blue]FUNCTION CALL:[/blue] show_reasoning()")
    for i, step in enumerate(input.steps, 1):
        console.print(Panel(
            f"{step}",
            title=f"Step {i}",
            border_style="cyan"
        ))
    
    # Create a TextContent object
    return TextContent(type="text", text="Reasoning shown")
    

@mcp.tool()
def create_thumbnail(input: CreateThumbnailInput) -> Image:
    """Create a thumbnail from an image"""
    print("CALLED: create_thumbnail(image_path: str) -> Image:")
    img = PILImage.open(input.image_path)
    img.thumbnail((100, 100))
    # return CreateThumbnailOutput(result=Image(data=img.tobytes(), format="png"))
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(input: StringToAsciiInput) -> StringToAsciiOutput:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(input: StringToAsciiInput) -> StringToAsciiOutput:")
    return StringToAsciiOutput(result=[int(ord(char)) for char in input.string])

@mcp.tool()
def int_list_to_exponential_sum(input: ExponentialSumInput) -> ExponentialSumOutput:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(input: ExponentialSumInput) -> ExponentialSumOutput:")
    return ExponentialSumOutput(result=sum(math.exp(i) for i in input.int_list))

@mcp.tool()
def fibonacci_numbers(input: FibonacciInput) -> FibonacciOutput:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(input: FibonacciInput) -> FibonacciOutput:")
    if input.n <= 0:
        return FibonacciOutput(result=[])
    fib_sequence = [0, 1]
    for _ in range(2, input.n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return FibonacciOutput(result=fib_sequence[:input.n])

@mcp.tool()
def open_keynote() -> OpenKeynoteOutput:
    """Opens the keynote app and creates a new document in the macbook. Returns True if successful, False otherwise."""
    print("CALLED: open_keynote() -> OpenKeynoteOutput")
    apple_script = '''
    tell application "Keynote"
        activate
        set thisDocument to make new document with properties {document theme:theme "White"}
        tell thisDocument
            set base slide of the first slide to master slide "Blank"
        end tell
    end tell
    '''
    result = subprocess.run(["osascript", "-e", apple_script],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print("Error:", result.stderr)
        return OpenKeynoteOutput(success = False)
    print("Keynote opened and new document created.")
    return OpenKeynoteOutput(success = True)

@mcp.tool()
def draw_rectangle_in_keynote(input: KeynoteRectangleInput = KeynoteRectangleInput(shapeHeight=100, shapeWidth=100)) -> KeynoteRectangleOutput:
    """Draws a rectangle in keynote app of the provided size. Returns True if rectangle is drawn successfully, False otherwise."""
    print("CALLED: draw_rectangle_in_keynote(input: KeynoteRectangleInput) -> KeynoteRectangleOutput:")
    apple_script = f'''
    tell application "Keynote"
        tell document 1
            set docWidth to its width
            set docHeight to its height
            set x to (docWidth - {{{input.shapeWidth}}}) div 2
            set y to (docHeight - {{{input.shapeHeight}}}) div 2
            tell slide 1
                set newRectangle to make new shape with properties {{position:{{x, y}}, width:{input.shapeWidth}, height:{input.shapeHeight}}}
            end tell
        end tell
    end tell
    '''
    result = subprocess.run(["osascript", "-e", apple_script],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print("Draw rectangle error:", result.stderr)
        return KeynoteRectangleOutput(success=False)
    print("Rectangle drawn on the slide.")
    return KeynoteRectangleOutput(success=True)

@mcp.tool()
def add_text_to_keynote_shape(input: KeynoteTextInput) -> KeynoteTextOutput:
    """Adds a text to the shape drawn in keynote. Return True if text was added successfully, False otherwise."""
    print("CALLED: add_text_to_keynote_shape(input: KeynoteTextInput) -> KeynoteTextOutput:")
    apple_script = f'''
    tell application "Keynote"
        tell document 1
            tell slide 1
                set the object text of the shape 1 to "{input.text}"
            end tell
        end tell
    end tell
    '''
    result = subprocess.run(["osascript", "-e", apple_script],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print("Add text error:", result.stderr)
        return KeynoteTextOutput(success=False)
    print("Text added to the rectangle.")
    return KeynoteTextOutput(success=True)

# DEFINE RESOURCES

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"


# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    print("CALLED: review_code(code: str) -> str:")
    return f"Please review this code:\n\n{code}"
    

@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

def start_sse():
    mcp_server = mcp._mcp_server  # noqa: WPS437
    import argparse
    from pdb import set_trace

    # set_trace()
    parser = argparse.ArgumentParser(description='Run MCP SSE-based server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=7172, help='Port to listen on')
    args = parser.parse_args()
    print("SSE args set.")

    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)
    app.mount("/", starlette_app)

    uvicorn.run(app, host=args.host, port=args.port) 

@app.get("/")
def read_root():
    return {"Hello": "Worlddd"}

@app.get("/mcp")
async def get_capabilites():
    return await mcp.list_tools()


if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING")
    if len(sys.argv) > 1:
        if sys.argv[1] == "dev":
            print("STARTING without transport for dev server")
            mcp.run() 
        elif sys.argv[1] == "sse":
            sys.argv.remove("sse")
            print("STARTING sse server")
            start_sse()
     # Run without transport for dev server
    else:
        print("STARTING with stdio for direct execution")
        mcp.run(transport="stdio")
else: 
    print("starting sse...")
    start_sse()
        

 # Run with stdio for direct execution
