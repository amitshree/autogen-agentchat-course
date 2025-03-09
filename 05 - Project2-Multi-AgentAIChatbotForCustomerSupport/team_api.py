from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from teams import main  # Importing the async function from team.py

app = FastAPI()

# Define request schema
class ChatRequest(BaseModel):
    query: str  # Expecting a JSON request with a 'query' field

@app.post("/chat/")
async def chat(request: ChatRequest):  # Accepts JSON body
    response = await main(request.query)  # Extract query from request body
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
