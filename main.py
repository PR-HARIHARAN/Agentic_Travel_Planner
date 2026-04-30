from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent.agentic_workflow import GraphBuilder
from starlette.responses import JSONResponse
from typing import Any, Dict, List
import os
from dotenv import load_dotenv
from pydantic import BaseModel
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # set specific origins in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class QueryRequest(BaseModel):
    question: str


def _build_agent_trace(messages: List[Any]) -> List[Dict[str, str]]:
    """Extract a simple execution trace suitable for frontend rendering."""
    trace: List[Dict[str, str]] = []

    for message in messages:
        message_type = getattr(message, "type", "")

        if message_type == "human":
            trace.append({"stage": "input", "label": "User Request", "detail": str(getattr(message, "content", ""))})

        elif message_type == "ai":
            tool_calls = getattr(message, "tool_calls", None) or []
            if tool_calls:
                for call in tool_calls:
                    name = call.get("name", "unknown_tool")
                    args = call.get("args", {})
                    trace.append(
                        {
                            "stage": "tool-call",
                            "label": f"Calling {name}",
                            "detail": str(args),
                        }
                    )
            elif getattr(message, "content", ""):
                trace.append(
                    {
                        "stage": "reasoning",
                        "label": "Agent Response Draft",
                        "detail": str(getattr(message, "content", "")),
                    }
                )

        elif message_type == "tool":
            trace.append(
                {
                    "stage": "tool-result",
                    "label": f"Tool Result: {getattr(message, 'name', 'tool')}",
                    "detail": str(getattr(message, "content", "")),
                }
            )

    return trace

@app.post("/query")
async def query_travel_agent(query:QueryRequest):
    try:
        print(query)
        graph = GraphBuilder(model_provider="groq")
        react_app=graph()
        #react_app = graph.build_graph()

        png_graph = react_app.get_graph().draw_mermaid_png()
        with open("my_graph.png", "wb") as f:
            f.write(png_graph)

        print(f"Graph saved as 'my_graph.png' in {os.getcwd()}")
        # Assuming request is a pydantic object like: {"question": "your text"}
        messages={"messages": [query.question]}
        output = react_app.invoke(messages)

        # If result is dict with messages:
        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content  # Last AI response
            trace = _build_agent_trace(output["messages"])
        else:
            final_output = str(output)
            trace = [{"stage": "response", "label": "Agent Response", "detail": final_output}]
        
        return {"answer": final_output, "agent_trace": trace}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})