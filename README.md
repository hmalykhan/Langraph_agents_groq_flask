# Class 05 — One Agent with LangGraph, Groq and Flask

**Goal:** Make ONE LangGraph agent that chooses between TWO tools and remembers earlier messages in the same chat.

## 1. Small architecture

```text
User -> Flask POST /chat -> LangGraph agent -> Groq model
                               |                |
                               |  tool needed?  |
                               v                |
                            Tools node <--------+
                               |
                               +-> back to agent -> final response -> Flask -> User
```

- **Agent node:** Calls Groq. It returns a message (possibly requesting a tool).
- **Tools node:** Runs the requested Python tool.
- **Conditional edge:** Sends the request to tools if needed; otherwise finishes.
- **MessagesState:** Adds new messages to conversation history.
- **InMemorySaver + thread_id:** Keeps different chats separate while Flask remains running.

## 2. Files

```text
langgraph_single_agent_groq_flask/
├── app.py          # Flask: one POST endpoint
├── graph.py        # LangGraph: one agent, tools node, memory
├── tools.py        # Two tools; SQLite complaint storage
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 3. Run in 5 steps

1. Open this folder in a terminal. Create environment: `python -m venv .venv`.
2. Activate it: Windows PowerShell `.venv\Scripts\Activate.ps1`; macOS/Linux `source .venv/bin/activate`.
3. Install: `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env`, then put your real `GROQ_API_KEY` in `.env` (never commit this file).
5. Start Flask: `python app.py` (runs on `http://127.0.0.1:5000`).

## 4. Test with Postman (Body -> raw -> JSON)

**Method and URL:** `POST http://127.0.0.1:5000/chat`

**Test A — read policy**
```json
{"session_id":"student-1","message":"What is the attendance policy?"}
```

**Test B — create complaint**
```json
{"session_id":"student-1","message":"Create a complaint: Wi-Fi is broken in Lab 2."}
```

**Test C — memory (same session)**
```json
{"session_id":"student-1","message":"What did I complain about earlier?"}
```

**Test D — separate chat**
```json
{"session_id":"student-2","message":"What did I complain about earlier?"}
```

The answer in Test D should not include messages from `student-1`.

## 5. Full request path (easy words)

1. Postman sends JSON to Flask.
2. Flask uses `session_id` as LangGraph's `thread_id`.
3. LangGraph loads messages for that chat.
4. The agent asks Groq what to do.
5. If Groq asks for a tool, LangGraph runs it and loops back to the agent.
6. The agent returns a final message. Flask returns it as JSON.

## 6. Important for students

- The model **chooses** tools; the **Python server runs** them.
- Chat messages live in `InMemorySaver`, so they disappear after Flask restarts.
- Complaints live in `complaints.db` (SQLite), so they survive restarts.
- This is a simple educational demo: no login, authentication, RAG, streaming or frontend yet.
- Policy rules are **fictional sample data**. Do not present them as real university rules.

### Learning challenge

Explain why `agent_node()` returns `{'messages': [response]}`, and why the edge from `tools` goes back to `agent`.

## Docs

- [LangGraph quickstart](https://docs.langchain.com/oss/python/langgraph/quickstart)
- [LangGraph memory](https://docs.langchain.com/oss/python/langgraph/add-memory)
- [Groq GPT-OSS 120B](https://console.groq.com/docs/model/openai/gpt-oss-120b)
