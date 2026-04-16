import asyncio
import os

from core.config import setup_api_key
setup_api_key()

from agents.agent import create_unsafe_agent
from attacks.attacks import run_attacks
import traceback

async def main():
    agent, runner = create_unsafe_agent()
    print("Testing if run_attacks throws google error...")
    try:
        await run_attacks(agent, runner)
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
