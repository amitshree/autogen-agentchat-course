from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core import CancellationToken
import asyncio

# Initialize OpenAI client
model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

# Initialize Autogen Agent
code_expert = AssistantAgent(
    name="CodeExpert",
    system_message="You are an expert in analyzing and debugging code. Your job is to explain, debug, and suggest improvements.",
    model_client=model_client
)

async def get_code_explanation(code: str) -> str:
    """AI-powered explanation of the provided Python code."""
    message = TextMessage(content= f"Explain the following Python code:\n\n{code}", source= "user")
    response = await code_expert.on_messages(messages=[message], cancellation_token=CancellationToken())
    print(response)
    return response.chat_message.content

async def get_code_optimization(code: str) -> str:
    """AI-powered optimization suggestions for the provided Python code."""
    optimization_prompt = f"Optimize the following Python function for efficiency:\n\n{code}"
    prompt = TextMessage(content=optimization_prompt, source="user")
    response = await code_expert.on_messages(messages=[prompt], cancellation_token=CancellationToken())
    return response.chat_message.content
    