
import ast
from asyncio import log
import asyncio
import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai
from pdb import set_trace

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

class MemoryItem(BaseModel):
    text: str

class MemoryManager:
    def __init__(self) -> None:
        self.facts: List[MemoryItem] = []
    
    def store(self, fact: MemoryItem):
        self.facts.append(fact)
    
    async def recall(self, query) -> List[MemoryItem]:
        if (not self.facts):
            return []

        prompt = f"""
You are given a list of memory items in the form of MemoryItem(text='...'). Each item contains a factual sentence.

Given the following list of memory items:
{self.facts}

And the query: {query}

Select and return only the relevant memory items whose content directly relates to the query.
Important instructions:

    Do not generate or include any code.

    Do not explain your choices.

    Do not modify, correct, or rephrase any of the memory texts.

    Only include the exact text values from relevant memory items.

    Your output must only be the list of strings, like this:

Output format:

[
    'Capital of india is delhi',
    'Hindi is the largest spoken language',
    'Modi is the PM of india'
]
"""
        try:
            response = await call_llm_with_timeout(client, prompt)
            raw = response.text.strip()
            # print(f"LLM output: {raw}")
            # set_trace()
            log("memory", f"LLM output: {str(raw)}")

            text_items = ast.literal_eval(str(raw))

            memory_items: List[MemoryItem] = [MemoryItem(text=t) for t in text_items]

            return memory_items
        except Exception as e:
            log("memory", f"⚠️ Memory recall failed: {e}")
            return []

        # return call_llm(prompt)


if __name__ == "__main__":
    mItem1 = MemoryItem(text="Capital of india is delhi")
    mItem2 = MemoryItem(text="Singapor is an island conuntry")
    mItem3 = MemoryItem(text="Saturn has rings")
    mItem4 = MemoryItem(text="Hindi is the largest spoken language")
    mItem5 = MemoryItem(text="Modi is the PM of india")

    mem = MemoryManager()
    mem.store(mItem1)
    mem.store(mItem2)
    mem.store(mItem3)
    mem.store(mItem4)
    mem.store(mItem5)

    rec = asyncio.run(mem.recall("Tell few facts about India."))
    print(rec)
