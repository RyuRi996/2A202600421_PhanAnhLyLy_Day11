from google.genai import Client
import inspect

c = Client(api_key="none")
print("Type of c.models:", type(c.models))
print("Has generate_content:", hasattr(c.models, "generate_content"))
