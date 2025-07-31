# Importing necessary libraries
from langchain import hub as prompts
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage

from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, MessagesState, StateGraph

from .tools.vector_store import vector_store

import os
from dotenv import load_dotenv

load_dotenv()

@tool
def upsert_candidate(name: str, email: str, resume: str):
    """
    Use this tool to insert a candidate into the vector database.

    This tool requires the following information:
    - name: str
    - email: str
    - resume: str
    """
    vector_store.upsert_candidate(name, email, resume)
    return f"Candidate {name} with email {email} and resume {resume} inserted successfully."

@tool
def search_candidate(query: str):
    """
    Use this tool to search for a candidate in the vector database according to the query.

    This tool requires the following information:
    - query: str
    """
    return vector_store.search_candidate(query)

@tool
def upsert_company(company_name: str, job_title: str, company_query: str):
    """
    Use this tool to insert a company along with its query and wanted job title into the vector database.

    This tool requires the following information:
    - company_name: str
    - job_title: str
    - company_query: str
    """
    vector_store.upsert_company(company_name, job_title, company_query)
    return f"Company {company_name} that wants a {job_title} and with the query {company_query} inserted successfully."

@tool
def search_company(query: str):
    """
    Use this tool to search for a company in the vector database according to the query from the job seeker.

    This tool requires the following information:
    - query: str
    """
    return vector_store.search_company(query)

# Create a model
model = init_chat_model(
    "gpt-4o",
    model_provider="openai",
    temperature=0,
    verbose=True
)

tools = [upsert_candidate, search_candidate, upsert_company, search_company]
tool_node = ToolNode(tools)

# Bind tools to the LLM
model_with_tool = model.bind_tools(tools)

# Pull the prompt template from the hub
prompt_template = prompts.pull("tha-prompt:latest", api_key=os.getenv("LANGCHAIN_API_KEY"))

# Create a model with tools
llm_chain = (prompt_template | model_with_tool)

# Create a function to call the model
def call_model(state: MessagesState, config: RunnableConfig):
    response = llm_chain.invoke(state, config=config)
    return {"messages": response}

# Create memory saver(memory)
memory = MemorySaver()

# Create a graph
agent_graph = StateGraph(state_schema=MessagesState)

# Add graph nodes
agent_graph.add_node("model", call_model)
agent_graph.add_node("tools", tool_node)

# Add edges
agent_graph.add_edge(START, "model")
agent_graph.add_conditional_edges("model", tools_condition, ["tools", END])
agent_graph.add_edge("tools", "model")

# Compile the graph
graph = agent_graph.compile(checkpointer=memory)
