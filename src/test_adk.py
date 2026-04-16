import asyncio
from unittest.mock import patch, MagicMock

import google.adk.runners as runners
from google.adk.agents import llm_agent

async def main():
    agent = llm_agent.LlmAgent(model="gemini-2.5-flash-lite", name="test_agent", instruction="You are an assistant.")
    runner = runners.InMemoryRunner(agent=agent, app_name="test")
    
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Mocked response"
    mock_part = MagicMock()
    mock_part.text = "Mocked response"
    mock_content = MagicMock()
    mock_content.parts = [mock_part]
    mock_response.content = mock_content
    
    # Needs async generator
    async def fake_stream(*args, **kwargs):
        print("Called generate_content_stream with kwargs:", kwargs)
        yield mock_response
        
    mock_client.models.generate_content_stream = fake_stream
    
    with patch("google.adk.runners.in_memory.in_memory.genai.Client", return_value=mock_client) as mock_cls:
        try:
            async for event in runner.run_async(user_id="test", session_id="123", new_message="hello"):
                print("Event:", event)
                if hasattr(event, "content"):
                    for p in event.content.parts:
                        print("- Part:", getattr(p, "text", p))
        except Exception as e:
            print("Error running ADK:", e)

if __name__ == "__main__":
    asyncio.run(main())
