from contextlib import asynccontextmanager
from typing import List, Tuple, AsyncGenerator
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse

from .config import settings
from .agent.tools.vector_store import VectorStore
from .agent.agent import graph

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel

class Message(BaseModel):
    role: str  # 'human', 'ai', etc.
    content: str

class AgentRequest(BaseModel):
    messages: List[Message]
    user_id: str = "user_123"
    thread_id: str = "conversation_1"
    temperature: float = 0.0

class AgentResponse(BaseModel):
    response: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing VectorStore...")
    app.state.vector_store = VectorStore(settings)
    print("VectorStore initialized successfully")
    
    yield
    
    # Shutdown
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

# Dependency function
def get_vector_store() -> VectorStore:
    return app.state.vector_store

@app.get("/healthcheck")
def healthcheck():
    return {"message": "OK"}

async def generate_response(messages: List[Tuple[str, str]], user_id: str, thread_id: str, temperature: float) -> AsyncGenerator[str, None]:
    config = RunnableConfig(
        configurable={
            "thread_id": thread_id,
            "user_id": user_id,
            "temperature": temperature,
        },
        recursion_limit=25
    )

    # Invoke the LangGraph agent
    for output, metadata in graph.stream({"messages": messages}, config=config, stream_mode="messages"):
        if hasattr(output, "content") and metadata['langgraph_node'] == 'model':                                           
            yield output.content

@app.post("/chat")
async def chat(request: AgentRequest):
    # Convert to LangGraph's MessagesState format (list of tuples)
    messages: List[Tuple[str, str]] = [(msg.role, msg.content) for msg in request.messages]

    async def stream_response():
        async for chunk in generate_response(messages, request.user_id, request.thread_id, request.temperature):
            yield chunk

    return StreamingResponse(stream_response(), media_type="text/event-stream")