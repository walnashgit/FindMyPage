
import asyncio
import os
import re
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai

from llm import call_llm_with_timeout

try:
    from agent import log
except ImportError:
    import datetime
    def log(stage: str, msg: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] [{stage}] {msg}")

load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


class PerceptionResult(BaseModel):
    user_input: str
    objective: Optional[str]
    objects: List[str] 
    tool_hint: Optional[str]


async def extract_perception(user_input: str) -> PerceptionResult:
    """Extracts objective, objects, and tool hints using LLM"""

    prompt = f"""You are an AI that extracts structured facts from user input and returns them as a valid Python dictionary.

Input: "{user_input}"

Your response must be a valid single-line Python dictionary with the following keys:

- "objective": A short string summarizing the user's goal.
- "objects": A list of strings representing keywords, values, or relevant facts (e.g., ["INDIA", "ASCII"]). This must always be a list, even if empty.
- "tool_hint": A string representing the name of the MCP tool that might help — use null if there's no obvious tool.

⚠️ Requirements:
- Output only the dictionary (no markdown, no code blocks, no extra text).
- All keys must be present in the dictionary, even if some values are null or empty.
- Ensure "objects" is always a list of strings.
- Ensure "tool_hint" is either a string (e.g., "Calculator") or "null" — do not use empty lists or other types.

Output example:
{{"objective": "calculate the sum", "objects": ["4", "5"], "tool_hint": "Calculator"}}"""
    try:
        response = await call_llm_with_timeout(client, prompt)
        raw = response.text.strip()
        log("perception", f"LLM output: {raw}")

        # Strip Markdown backticks if present
        clean = re.sub(r"^```json|```$", "", raw.strip(), flags=re.MULTILINE).strip()

        try:
            parsed = eval(clean)
        except Exception as e:
            log("perception", f"⚠️ Failed to parse cleaned output: {e}")
            raise

        # Fix common issues
        if isinstance(parsed.get("objects"), dict):
            parsed["objects"] = list(parsed["objects"].values())

        # Fix `tool_hint` type if it's a list
        if isinstance(parsed.get("tool_hint"), list):
            # Join list to string or just set to None if empty
            parsed["tool_hint"] = ", ".join(parsed["tool_hint"]) if parsed["tool_hint"] else None

        return PerceptionResult(user_input=user_input, **parsed)
    except Exception as e:
        log("perception", f"⚠️ Extraction failed: {e}")
        return PerceptionResult(user_input=user_input)

if __name__ == "__main__":
    print("\nEnter your query (or 'exit' to quit):")
    query = input("> ")
    res = asyncio.run(extract_perception(query))
    print(res)