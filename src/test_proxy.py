import asyncio
from core.config import setup_api_key
setup_api_key()

from google.genai import Client

async def main():
    print("Testing if Client reaches OpenAI or Gemini...")
    c = Client()
    print("Base URL:", c._http_options.base_url if hasattr(c, "_http_options") else "N/A")
    resp = c.models.generate_content(model="gemini-2.5-flash", contents="say hello")
    print("Response:", resp.text)

if __name__ == "__main__":
    asyncio.run(main())
