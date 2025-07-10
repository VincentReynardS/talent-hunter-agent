# Importing necessary libraries
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage

from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, MessagesState, StateGraph

from ..config import settings
from .tools.vector_store import vector_store

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

system_prompt = """
You are a helpful talent hunter that helps job seekers find their dream jobs.
You are given a job seeker's query and you need to find the best job for them.
Additionally, you also help companies find the best candidates for their jobs.

You have access to the following tools:
- insert_candidate: to insert a candidate into the vector database
- search_candidate: to search for a candidate in the vector database
- insert_company: to insert a company into the vector database
- search_company: to search for a company in the vector database

You need to use the tools to find the best job for the job seeker.
You need to use the tools to find the best candidates for the company.

The tools may require some information to be inserted into the vector database.
You need to ask the job seeker for the information if the tools require it.

Sometimes, the job that a job seeker is looking for is not available in the vector database.
In this case, just inform the job seeker that the job is not available and ask them to come back later.

Likewise, if a suitable candidate is not available for a company, just inform the company that the candidate is not available and ask them to come back later.
"""

# Create a prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "{input}")
])

# Create a model with tools
llm_chain = prompt_template | model_with_tool

# Create a function to call the model
def call_model(state: MessagesState, config: RunnableConfig):
    response = llm_chain.invoke({"input": state["messages"]})
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
