from fastapi import FastAPI
from pydantic import BaseModel
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

app = FastAPI()

# Mock E-commerce API Functions
def fetch_order_status(order_id: str) -> str:
    return f"Order {order_id} is currently in transit and will be delivered by tomorrow."

def fetch_product_availability(product_name: str) -> str:
    return f"The product '{product_name}' is available in stock at $99."

def register_complaint(order_id: str, issue: str) -> str:
    return f"Complaint registered for order {order_id}: {issue}. Our support team will contact you soon."

def place_order(product_name: str, quantity: int) -> str:
    return f"Order placed successfully for {quantity} unit(s) of '{product_name}'."

# Define Model
model_client = OpenAIChatCompletionClient(model="gpt-4o")

# Define Agents
order_inquiry_agent = AssistantAgent(
    "OrderInquiryAgent",
    description="Handles order status inquiries.",
    tools=[fetch_order_status],
    model_client=model_client,
    system_message="You provide order status updates using fetch_order_status().",
)

product_inquiry_agent = AssistantAgent(
    "ProductInquiryAgent",
    description="Handles product availability and pricing queries.",
    tools=[fetch_product_availability],
    model_client=model_client,
    system_message="You provide product availability updates using fetch_product_availability().",
)

complaint_resolution_agent = AssistantAgent(
    "ComplaintResolutionAgent",
    description="Handles complaints related to orders (returns, refunds).",
    tools=[register_complaint],
    model_client=model_client,
    system_message="You register complaints using register_complaint().",
)

order_placement_agent = AssistantAgent(
    "OrderPlacementAgent",
    description="Helps users place new orders.",
    tools=[place_order],
    model_client=model_client,
    system_message="You place orders using place_order().",
)

chat_orchestrator = AssistantAgent(
    "ChatOrchestrator",
    description="Decides which agent should respond based on query type.",
    model_client=model_client,
    system_message="You assign customer queries to the correct agent.",
)

# SelectorGroupChat for Agent Coordination
team = SelectorGroupChat(
    [
        chat_orchestrator,
        order_inquiry_agent,
        product_inquiry_agent,
        complaint_resolution_agent,
        order_placement_agent,
    ],
    model_client=model_client,
    selector_prompt="Determine the best agent to handle the customer's request.",
    allow_repeated_speaker=True,
)

# FastAPI Endpoint for Handling Chat
class QueryInput(BaseModel):
    query: str

@app.post("/chat")
async def chat_endpoint(query_input: QueryInput):
    response = await team.run_stream(task=query_input.query)
    return {"response": response}
