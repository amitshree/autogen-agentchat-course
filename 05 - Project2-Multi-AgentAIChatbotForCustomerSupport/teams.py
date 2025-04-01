from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
import asyncio

# Sample product catalog with specific product names
PRODUCT_CATALOG = {
    "Dell XPS 15": {"price": 1500, "stock": 10},
    "Apple iPhone 15 Pro": {"price": 1200, "stock": 15},
    "Sony WH-1000XM5 Headphones": {"price": 350, "stock": 20},
    "Samsung Galaxy Tab S9": {"price": 900, "stock": 12},
    "Logitech MX Master 3S Mouse": {"price": 100, "stock": 30},
}

# Sample order database
ORDERS_DB = {
    "ORD-1": {"product": "Dell XPS 15", "quantity": 1, "customer_id": "CUST-001", "status": "Shipped"},
    "ORD-2": {"product": "Apple iPhone 15 Pro", "quantity": 2, "customer_id": "CUST-002", "status": "Processing"},
}

# Sample complaint database
COMPLAINTS_DB = {
    "CMP-1": {"order_id": "ORD-1", "customer_id": "CUST-001", "complaint": "Received a defective product.", "status": "Resolved"},
    "CMP-2": {"order_id": "ORD-2", "customer_id": "CUST-002", "complaint": "Order delayed.", "status": "Pending"},
}


# Function to find the closest matching product based on substring search
def find_closest_product(product_name: str) -> str:
    """Find the closest matching product from the catalog based on substring search."""
    for product in PRODUCT_CATALOG.keys():
        if product_name.lower() in product.lower():
            return product
    return None

# Product inquiry tool
def product_inquiry_tool(product_name: str) -> str:
    """Check product information using product name"""
    closest_product = find_closest_product(product_name)
    if closest_product:
        product = PRODUCT_CATALOG[closest_product]
        return f"{closest_product}: Price = ${product['price']}, Stock = {product['stock']} units."
    return f"Sorry, {product_name} is not available in our catalog."

# Order placement tool
def order_placement_tool(product_name: str, quantity: int = None, customer_id: str = "Guest") -> str:
    """Place order"""
    closest_product = find_closest_product(product_name)
    if not closest_product:
        return f"Sorry, {product_name} is not available."

    if quantity is None:
        return "MISSING_INFO: Please provide the quantity to place your order."

    product = PRODUCT_CATALOG[closest_product]
    if product["stock"] < quantity:
        return f"Only {product['stock']} units of {closest_product} are available."

    # Deduct stock and generate order ID
    product["stock"] -= quantity
    order_id = f"ORD-{len(ORDERS_DB) + 1}"
    ORDERS_DB[order_id] = {"product": closest_product, "quantity": quantity, "customer_id": customer_id, "status": "Processing"}
    
    return f"Order placed successfully! Order ID: {order_id}"

# Order status tool
def order_status_tool(order_id: str) -> str:
    """Check order status"""
    order = ORDERS_DB.get(order_id)
    if order:
        return f"Order ID: {order_id}, Product: {order['product']}, Quantity: {order['quantity']}, Status: {order['status']}."
    return "Invalid Order ID."

# Complaint registration tool
def complaint_registration_tool(order_id: str, complaint_text: str, customer_id: str = "Guest") -> str:
    """Register complaint"""
    if order_id not in ORDERS_DB:
        return "Invalid Order ID. Cannot register complaint."

    complaint_id = f"CMP-{len(COMPLAINTS_DB) + 1}"
    COMPLAINTS_DB[complaint_id] = {"order_id": order_id, "customer_id": customer_id, "complaint": complaint_text, "status": "Pending"}

    return f"Complaint registered successfully! Complaint ID: {complaint_id}"

# Initialize Model Client
model_client = OpenAIChatCompletionClient(model="gpt-4o")

# Define Agents

planning_agent = AssistantAgent(
    "PlanningAgent",
    description="An agent that plans customer support tasks and delegates to appropriate agents.",
    model_client=model_client,
    system_message="""
    You are a planning agent.
    Your job is to identify customer requests and delegate them to the correct agent.
    Available agents:
        - ProductInquiryAgent: Handles product-related questions
        - OrderPlacementAgent: Handles order placement
        - OrderInquiryAgent: Checks order status
        - ComplaintAgent: Registers customer complaints
        - ResponseAgent: Responsible for responding to the user.

    Once a task is completed by another agent, delegate the response to the **ResponseAgent** to format and send the final reply to the user.
    
    Format task assignments as:
    1. <agent> : <task>
    """,
)

product_inquiry_agent = AssistantAgent(
    "ProductInquiryAgent",
    description="Handles product inquiries.",
    tools=[product_inquiry_tool],
    model_client=model_client,
    system_message="You provide product information using the product_inquiry_tool."
)

order_placement_agent = AssistantAgent(
    "OrderPlacementAgent",
    description="Handles order placement.",
    tools=[order_placement_tool],
    model_client=model_client,
    system_message="""
    You process orders using the order_placement_tool.
    
    If any details are missing to call the order_placement_tool, ask the customer for the missing details.
    """,
)

order_inquiry_agent = AssistantAgent(
    "OrderInquiryAgent",
    description="Handles order status inquiries.",
    tools=[order_status_tool],
    model_client=model_client,
    system_message="You check order status using the order_status_tool."
)

complaint_agent = AssistantAgent(
    "ComplaintAgent",
    description="Handles customer complaints.",
    tools=[complaint_registration_tool],
    model_client=model_client,
    system_message="You register complaints using the complaint_registration_tool."
)

response_agent = AssistantAgent(
    "ResponseAgent",
    description="Formats responses and sends them to the user.",
    model_client=model_client,
    system_message="""
    Your job is to format the response provided by other agents and return it to the user in a clear and friendly manner.
    Always end the conversation with 'TERMINATE'.
    
    Example:
    - If an order is placed, confirm it and include the order ID.
    - If a product inquiry is made, summarize the details.
    - If an order status is checked, summarize the response.
    - If a complaint is registered, confirm it with the complaint ID.
    """,
)

# Define termination conditions
text_mention_termination = TextMentionTermination("TERMINATE")
max_messages_termination = MaxMessageTermination(max_messages=10)
termination = text_mention_termination | max_messages_termination

# Create the Team
team = SelectorGroupChat(
    [
        planning_agent,
        product_inquiry_agent,
        order_placement_agent,
        order_inquiry_agent,
        complaint_agent,
        response_agent
    ],
    model_client=model_client,
    termination_condition=termination,
    allow_repeated_speaker=True,
)

async def main(query):
    #await Console(team.run_stream(task=query))
    response = await team.run(task=query)
    result = response.messages[-1].content

    # Remove 'TERMINATE' if it's at the end
    if result.endswith("TERMINATE"):
        result = result.removesuffix("TERMINATE").strip()

    return result

if __name__ == "__main__":
    print(asyncio.run(main("I want to buy Samsung Galaxy Tab of 3 quantity as a guest.")))
