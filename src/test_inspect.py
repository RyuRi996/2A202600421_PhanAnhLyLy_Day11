from google.adk.agents import llm_agent
import inspect

print("LlmAgent parameters:")
sig = inspect.signature(llm_agent.LlmAgent.__init__)
for name, param in sig.parameters.items():
    print(name, param.annotation)
