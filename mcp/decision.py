
import os
from typing import List, Optional

from dotenv import load_dotenv
from llm import call_llm_with_timeout
from memory import MemoryItem
from perception import PerceptionResult
from google import genai


try:
    from agent import log
except ImportError:
    import datetime
    def log(stage: str, msg: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] [{stage}] {msg}")

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)


async def generate_plan(
    perception: PerceptionResult,
    memory_items: List[MemoryItem],
    tool_descriptions: Optional[str] = None
) -> str:
    """Generates a plan (tool call or final answer) using LLM based on structured perception and memory."""

    memory_texts = "\n".join(f"- {m.text}" for m in memory_items) or "None"

    tool_context = f"\nYou have access to the following tools:\n{tool_descriptions}" if tool_descriptions else ""

    prompt = f"""
You are a reasoning-driven AI agent with access to tools. Your job is to solve the user's request step-by-step by reasoning through the problem, selecting a tool if needed, and continuing until the FINAL_ANSWER is produced.{tool_context}

Always follow this loop:

1. Think step-by-step about the problem.
2. Explicitly identify the type of reasoning you are using at each step (e.g., arithmetic, logic, lookup etc.).
3. ALWAYS provide reasoning before starting to solve a problem.
4. Provide reasoning for intermediate steps whereever necessary.
5. If a tool is needed, respond using the format:
   FUNCTION_CALL: {{"func_name":"function_name","param":{{"input":{{"param1":"value1", "param2":"value2"}}}}}}
6. When the final answer is known, respond using:
   FINAL_ANSWER: [your final result]
7. If uncertain or a tool fails, attempt a fallback approach and note it.

Guidelines:
- Respond using EXACTLY ONE of the formats above per step.
- Do NOT include extra text, explanation, or formatting.
- Use nested keys (e.g., input.string) and square brackets for lists.
- You can reference these relevant memories:
{memory_texts}

Input Summary:
- User input: "{perception.user_input}"
- Objective: {perception.objective}
- Objects: {', '.join(perception.objects)}
- Tool hint: {perception.tool_hint or 'None'}

✅ Examples:
Query: Solve (2 + 3) * 4
Assistant: FUNCTION_CALL: {{"func_name":"show_reasoning", "param":{{"input":{{"steps":["1. [arithmetic] First, solve inside parentheses: 2 + 3", "2. [arithmetic] Then multiply the result by 4"]}}}}}}
Query: Result is Reasoning shown. What should I do next?
Assistant: FUNCTION_CALL: {{"func_name":"add","param":{{"input":{{"a":2, "b":3}}}}}}
Query: Result is 5. What should I do next?
Assistant: FUNCTION_CALL: {{"func_name":"multiply","param":{{"input":{{"a":5, "b":4}}}}}}
User: Result is 20. What should I do next?
Assistant: FINAL_ANSWER: [20]

✅ Examples:
- User asks: "What's the relationship between Cricket and Sachin Tendulkar"
  - FUNCTION_CALL: {{"func_name":"search_documents", "param":{{"query":"relationship between Cricket and Sachin Tendulkar"}}}}
  - [receives a detailed document]
  - FINAL_ANSWER: [Sachin Tendulkar is widely regarded as the "God of Cricket" due to his exceptional skills, longevity, and impact on the sport in India. He is the leading run-scorer in both Test and ODI cricket, and the first to score 100 centuries in international cricket. His influence extends beyond his statistics, as he is seen as a symbol of passion, perseverance, and a national icon. ]


IMPORTANT:
- 🚫 Do NOT invent tools. Use only the tools listed below.
- 📄 If the question may relate to factual knowledge, use the 'search_documents' tool to look for the answer.
- 🧮 If the question is mathematical or needs calculation, use the appropriate math tool.
- 🤖 If the previous tool output already contains factual information, DO NOT search again. Instead, summarize the relevant facts and respond with: FINAL_ANSWER: [your answer]
- Only repeat `search_documents` if the last result was irrelevant or empty.
- ❌ Do NOT repeat function calls with the same parameters.
- ❌ Do NOT output unstructured responses.
- 🧠 Think before each step. Verify intermediate results mentally before proceeding.
- 💥 If unsure or no tool fits, skip to FINAL_ANSWER: [unknown]
- 💥 In case of tool failure or ambiguous input, output: FALLBACK: [brief description of the issue and next step]
- ✅ You have only 3 attempts. Final attempt must be FINAL_ANSWER]
"""

    try:
        # response = client.models.generate_content(
        #     model="gemini-2.0-flash",
        #     contents=prompt
        # )
        response = await call_llm_with_timeout(client, prompt)
        raw = response.text.strip()
        log("plan", f"LLM output: {raw}")

        for line in raw.splitlines():
            if line.strip().startswith("FUNCTION_CALL:") or line.strip().startswith("FINAL_ANSWER:"):
                return line.strip()

        return raw.strip()

    except Exception as e:
        log("plan", f"⚠️ Decision generation failed: {e}")
        return "FINAL_ANSWER: [unknown]"