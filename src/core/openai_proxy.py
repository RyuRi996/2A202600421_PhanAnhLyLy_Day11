import os
import asyncio
from google.genai import types
import google.genai.models as genai_models

def patch_genai_for_openai():
    """
    Monkey-patches google.genai.models.Models to route all model calls to OpenAI's API.
    """
    from openai import AsyncOpenAI, OpenAI

    print("--- INJECTING OPENAI PROXY INTO GOOGLE GENAI ---")
    
    async_openai = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY", "missing_openai_key"))
    sync_openai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "missing_openai_key"))

    def _convert_to_openai_messages(kwargs_dict, contents):
        messages = []
        if "config" in kwargs_dict and hasattr(kwargs_dict["config"], "system_instruction"):
            si = kwargs_dict["config"].system_instruction
            if si is not None:
                if isinstance(si, types.Content):
                    text = "".join(p.text for p in si.parts if hasattr(p, 'text') and p.text)
                    messages.append({"role": "system", "content": text})
                elif isinstance(si, str):
                    messages.append({"role": "system", "content": si})

        if contents:
            if not isinstance(contents, list):
                contents = [contents]
            for c in contents:
                if isinstance(c, types.Content):
                    role = "user" if c.role == "user" else "assistant"
                    text = "".join(p.text for p in c.parts if hasattr(p, 'text') and p.text)
                    if text:
                        messages.append({"role": role, "content": text})
                elif isinstance(c, str):
                    messages.append({"role": "user", "content": c})
        
        # fallback if messages is empty
        if not messages:
            messages.append({"role": "user", "content": "hello"})
            
        return messages

    async def patched_generate_content_stream(self, *args, **kwargs):
        model = args[0] if len(args) > 0 else kwargs.get("model", "gpt-4o-mini")
        contents = args[1] if len(args) > 1 else kwargs.get("contents", [])
        
        messages = _convert_to_openai_messages(kwargs, contents)
        
        response_stream = await async_openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
            temperature=0.0
        )
        
        class MockResponseChunk:
            def __init__(self, text):
                self.content = types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=text)]
                )

        async for chunk in response_stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield MockResponseChunk(chunk.choices[0].delta.content)

    def patched_generate_content(self, *args, **kwargs):
        model = args[0] if len(args) > 0 else kwargs.get("model", "gpt-4o-mini")
        contents = args[1] if len(args) > 1 else kwargs.get("contents", [])
        
        messages = _convert_to_openai_messages(kwargs, contents)
        
        response = sync_openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=False,
            temperature=0.0
        )
        
        class MockResponse:
            @property
            def text(self):
                return response.choices[0].message.content
            @property
            def content(self):
                return types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=response.choices[0].message.content)]
                )
            @property
            def function_calls(self):
                return None
            def model_dump_json(self, *args, **kwargs):
                return "{}"
            @property
            def usage_metadata(self):
                return None
            def __getattr__(self, name):
                return None
            @property
            def candidates(self):
                class MockCandidate:
                    def __init__(self, text):
                        self.content = types.Content(role="model", parts=[types.Part.from_text(text=text)])
                    @property
                    def finish_reason(self):
                        return "STOP"
                    def __getattr__(self, name):
                        return None
                return [MockCandidate(response.choices[0].message.content)]
        
        return MockResponse()

    async def patched_generate_content_async(self, *args, **kwargs):
        model = args[0] if len(args) > 0 else kwargs.get("model", "gpt-4o-mini")
        contents = args[1] if len(args) > 1 else kwargs.get("contents", [])
        
        messages = _convert_to_openai_messages(kwargs, contents)
        
        response = await async_openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=False,
            temperature=0.0
        )
        
        class MockResponse:
            @property
            def text(self):
                return response.choices[0].message.content
            @property
            def content(self):
                return types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=response.choices[0].message.content)]
                )
            @property
            def function_calls(self):
                return None
            def model_dump_json(self, *args, **kwargs):
                return "{}"
            @property
            def usage_metadata(self):
                return None
            def __getattr__(self, name):
                return None
            @property
            def candidates(self):
                class MockCandidate:
                    def __init__(self, text):
                        self.content = types.Content(role="model", parts=[types.Part.from_text(text=text)])
                    @property
                    def finish_reason(self):
                        return "STOP"
                    def __getattr__(self, name):
                        return None
                return [MockCandidate(response.choices[0].message.content)]
        
        return MockResponse()

    # Monkey patch the methods directly on the class
    genai_models.Models.generate_content_stream = patched_generate_content_stream
    genai_models.Models.generate_content = patched_generate_content
    
    if hasattr(genai_models, "AsyncModels"):
        genai_models.AsyncModels.generate_content_stream = patched_generate_content_stream
        genai_models.AsyncModels.generate_content = patched_generate_content_async
        
    print("--- SUCCESS: ALL GEMINI REQUESTS ARE NOW ROUTED TO GPT-4O-MINI ---")
