# Load environment variables from .env file
import asyncio
import os
from dotenv import load_dotenv
from google import genai

try:
    from agent import log
except ImportError:
    import datetime
    def log(stage: str, msg: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] [{stage}] {msg}")


load_dotenv()

# Access your API key and initialize Gemini client correctly
# api_key = os.getenv("GEMINI_API_KEY")
# client = genai.Client(api_key=api_key)

async def call_llm_with_timeout(client, prompt, timeout=10):
    """Generate content using llm with a timeout"""
    log("llm", "Starting LLM generation...")
    try:
        # Convert the synchronous generate_content call to run in a thread
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        log("llm", "LLM generation completed")
        return response
    except TimeoutError:
        log("llm", "LLM generation timed out!")
        raise
    except Exception as e:
        log("llm", f"Error in LLM generation: {e}")
        raise