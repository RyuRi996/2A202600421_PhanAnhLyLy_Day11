import asyncio
import os
os.environ["OPENAI_API_KEY"] = "sk-fake-key"
os.environ["GOOGLE_API_KEY"] = "mock_key_for_proxy"

from core.config import setup_api_key
setup_api_key()

from google.genai import types
from google.adk.agents import llm_agent
from google.adk.runners import InMemoryRunner

async def main():
    agent = llm_agent.LlmAgent(model="gemini-2.5-flash", name="test", instruction="hello")
    runner = InMemoryRunner(agent=agent, app_name="test")
    try:
        content = types.Content(role="user", parts=[types.Part.from_text(text="say hi")])
        async for event in runner.run_async(user_id="test", session_id="123", new_message=content):
            print("Event:", event)
            if hasattr(event, "content"):
                print("-", event.content.parts[0].text)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
