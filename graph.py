"""One LangGraph agent node + one tools node, with a simple loop."""
import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from tools import search_policy, create_complaint

load_dotenv()
if not os.getenv('GROQ_API_KEY'):
    raise RuntimeError('GROQ_API_KEY missing. Copy .env.example to .env and add your key.')

# ONE AI agent, connected to TWO real Python tools.
tools = [search_policy, create_complaint]
llm = ChatGroq(model='openai/gpt-oss-120b', temperature=0)
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = (
    'You are a helpful university helpdesk assistant. '
    'For attendance, library, or fee policy questions, use search_policy first. '
    'If a student wants to file a complaint and explains the issue, use create_complaint. '
    'Never invent a policy or a ticket number. '
    'For questions about previous messages, use the existing chat history. '
    'Answer clearly and briefly.'
)


def agent_node(state: MessagesState):
    """Read history, ask Groq, and RETURN the new message to state."""
    response = llm_with_tools.invoke(
        [SystemMessage(content=SYSTEM_PROMPT)] + state['messages']
    )
    return {'messages': [response]}  # MessagesState APPENDS this message.


builder = StateGraph(MessagesState)
builder.add_node('agent', agent_node)
builder.add_node('tools', ToolNode(tools))

builder.add_edge(START, 'agent')
# If the model requested a tool -> tools. Otherwise -> END.
builder.add_conditional_edges('agent', tools_condition)
# After the tool runs, ask the same agent to give the final response.
builder.add_edge('tools', 'agent')

# Beginner memory: one history per thread_id. Resets on server restart.
graph = builder.compile(checkpointer=InMemorySaver())
