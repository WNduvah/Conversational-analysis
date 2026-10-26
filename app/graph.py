import json
from typing import TypedDict, Any

from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama

from .config import LOG_PATH, MODEL_NAME, OLLAMA_BASE_URL, MAX_RETRIES
from .database import schema_text, execute_read_only
from .prompts import SYSTEM_PROMPT, SUMMARY_PROMPT
from .security import validate_sql

class State(TypedDict, total=False):
    question: str
    sql: str
    valid: bool
    validation_error: str
    columns: list[str]
    rows: list[list[Any]]
    answer: str
    retries: int

def audit(event, payload):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"event": event, **payload}, default=str) + "\n")

def llm():
    return ChatOllama(model=MODEL_NAME, temperature=0, base_url=OLLAMA_BASE_URL)

def generate_sql(state):
    prompt = SYSTEM_PROMPT.format(schema=schema_text())

    if state.get("validation_error"):
        prompt += (
            "\nPrevious attempt failed. Fix it.\n"
            f"Reason: {state['validation_error']}\n"
            f"Previous SQL: {state.get('sql', '')}\n"
        )

    response = llm().invoke([
        ("system", prompt),
        ("human", state["question"]),
    ])

    sql = response.content.strip().replace("```sql", "").replace("```", "").strip()
    audit("sql_generated", {
        "question": state["question"],
        "sql": sql,
        "retry": state.get("retries", 0),
    })
    return {"sql": sql}

def validate(state):
    ok, result = validate_sql(state["sql"])

    if ok:
        audit("sql_validated", {"sql": result, "status": "approved"})
        return {"valid": True, "sql": result, "validation_error": ""}

    audit("sql_validated", {
        "sql": state["sql"],
        "status": "rejected",
        "reason": result,
    })
    return {
        "valid": False,
        "validation_error": result,
        "retries": state.get("retries", 0) + 1,
    }

def after_validation(state):
    if state["valid"]:
        return "execute"
    if state.get("retries", 0) <= MAX_RETRIES:
        return "generate"
    return "fail"

def execute(state):
    try:
        columns, rows = execute_read_only(state["sql"])
        audit("query_executed", {
            "sql": state["sql"],
            "row_count": len(rows),
            "status": "success",
        })
        return {"columns": columns, "rows": rows}
    except Exception as exc:
        audit("query_executed", {
            "sql": state["sql"],
            "status": "error",
            "error": str(exc),
        })
        return {
            "validation_error": f"Database error: {exc}",
            "retries": state.get("retries", 0) + 1,
            "valid": False,
        }

def after_execute(state):
    if "columns" in state:
        return "summarize"
    if state.get("retries", 0) <= MAX_RETRIES:
        return "generate"
    return "fail"

def summarize(state):
    response = llm().invoke(
        SUMMARY_PROMPT.format(
            question=state["question"],
            columns=state["columns"],
            rows=state["rows"],
        )
    )
    answer = response.content.strip()
    audit("answer_generated", {"question": state["question"]})
    return {"answer": answer}

def fail(state):
    return {
        "answer": (
            "I could not safely execute that question. "
            f"Reason: {state.get('validation_error', 'query failed')}"
        )
    }

def build_graph():
    graph = StateGraph(State)

    graph.add_node("generate", generate_sql)
    graph.add_node("validate", validate)
    graph.add_node("execute", execute)
    graph.add_node("summarize", summarize)
    graph.add_node("fail", fail)

    graph.add_edge(START, "generate")
    graph.add_edge("generate", "validate")
    graph.add_conditional_edges(
        "validate",
        after_validation,
        {"generate": "generate", "execute": "execute", "fail": "fail"},
    )
    graph.add_conditional_edges(
        "execute",
        after_execute,
        {"generate": "generate", "summarize": "summarize", "fail": "fail"},
    )
    graph.add_edge("summarize", END)
    graph.add_edge("fail", END)

    return graph.compile()
