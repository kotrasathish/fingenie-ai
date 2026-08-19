from typing import Literal

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from agent.state import AgentState
from agent.tools import calculate_emi

from rag.rag_service import rag_service
from services.ai.groq_service import groq_service


# ==========================================
# INTENT ROUTER
# ==========================================

def route_intent(
    state: AgentState
) -> AgentState:

    message = state["message"].lower()

    emi_keywords = [
        "emi",
        "monthly payment",
        "monthly installment",
        "loan calculation",
        "calculate loan",
        "loan payment",
        "monthly emi"
    ]

    rag_keywords = [
        "loan",
        "credit card",
        "cibil",
        "credit score",
        "interest rate",
        "personal loan",
        "home loan",
        "vehicle loan",
        "eligibility",
        "documents",
        "credit",
        "finance"
    ]

    if any(
        keyword in message
        for keyword in emi_keywords
    ):

        intent = "emi"

    elif any(
        keyword in message
        for keyword in rag_keywords
    ):

        intent = "rag"

    else:

        intent = "general"

    state["intent"] = intent

    return state


# ==========================================
# RAG NODE
# ==========================================

def rag_node(
    state: AgentState
) -> AgentState:

    result = rag_service.get_context(
        state["message"],
        k=4
    )

    state["context"] = result["context"]

    state["sources"] = result["sources"]

    return state


# ==========================================
# EMI NODE
# ==========================================

def emi_node(
    state: AgentState
) -> AgentState:

    message = state["message"]

    prompt = f"""
Extract the following information
from this user request:

{message}

Return ONLY valid JSON.

{{
    "principal": number,
    "annual_rate": number,
    "tenure_months": number
}}

If a value is missing, use 0.
"""

    extraction_messages = [

        {
            "role": "user",
            "content": prompt
        }

    ]

    from groq import Groq
    import os

    client = Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )

    response = client.chat.completions.create(

        model="qwen/qwen3.6-27b",

        messages=extraction_messages,

        temperature=0

    )

    import json

    text = response.choices[0].message.content

    # --------------------------------
    # Clean possible markdown JSON
    # --------------------------------

    text = text.strip()

    if text.startswith("```"):

        text = text.replace(
            "```json",
            ""
        )

        text = text.replace(
            "```",
            ""
        )

        text = text.strip()

    try:

        values = json.loads(text)

    except Exception:

        state["result"] = (
            "I need the loan amount, interest rate "
            "and tenure to calculate the EMI."
        )

        state["sources"] = []

        return state

    principal = float(
        values.get(
            "principal",
            0
        )
    )

    annual_rate = float(
        values.get(
            "annual_rate",
            0
        )
    )

    tenure_months = int(
        values.get(
            "tenure_months",
            0
        )
    )

    if principal <= 0:

        state["result"] = (
            "Please provide the loan amount."
        )

        state["sources"] = []

        return state

    if annual_rate <= 0:

        state["result"] = (
            "Please provide the annual interest rate."
        )

        state["sources"] = []

        return state

    if tenure_months <= 0:

        state["result"] = (
            "Please provide the loan tenure in months."
        )

        state["sources"] = []

        return state

    result = calculate_emi(

        principal,
        annual_rate,
        tenure_months

    )

    state["result"] = (

        f"### EMI Calculation\n\n"

        f"- **Loan Amount:** "
        f"₹{result['loan_amount']:,.2f}\n"

        f"- **Interest Rate:** "
        f"{result['interest_rate']}%\n"

        f"- **Tenure:** "
        f"{result['tenure_months']} months\n"

        f"- **Monthly EMI:** "
        f"₹{result['monthly_emi']:,.2f}\n"

        f"- **Total Interest:** "
        f"₹{result['total_interest']:,.2f}\n"

        f"- **Total Payment:** "
        f"₹{result['total_payment']:,.2f}"
    )

    state["sources"] = []

    return state


# ==========================================
# FINAL ANSWER
# ==========================================

def final_node(
    state: AgentState
) -> AgentState:

    # --------------------------------
    # Direct result
    # --------------------------------

    if state.get("result"):

        state["reply"] = state["result"]

        return state

    # --------------------------------
    # RAG Context
    # --------------------------------

    context = state.get(
        "context",
        ""
    )

    user_message = state["message"]

    messages = [

        {
            "role": "user",
            "content": user_message
        }

    ]

    reply = groq_service.ask(
        messages,
        context
    )

    # --------------------------------
    # Add sources
    # --------------------------------

    sources = state.get(
        "sources",
        []
    )

    if sources:

        source_names = []

        for source in sources:

            name = source["source"]

            if name not in source_names:

                source_names.append(name)

        reply += "\n\n### Sources\n"

        for source_name in source_names:

            reply += f"- `{source_name}`\n"

    state["reply"] = reply

    return state


# ==========================================
# ROUTING
# ==========================================

def choose_node(
    state: AgentState
) -> Literal[
    "rag",
    "emi",
    "final"
]:

    intent = state.get(
        "intent"
    )

    if intent == "rag":

        return "rag"

    if intent == "emi":

        return "emi"

    return "final"


# ==========================================
# BUILD GRAPH
# ==========================================

builder = StateGraph(
    AgentState
)


builder.add_node(
    "router",
    route_intent
)

builder.add_node(
    "rag",
    rag_node
)

builder.add_node(
    "emi",
    emi_node
)

builder.add_node(
    "final",
    final_node
)


builder.add_edge(
    START,
    "router"
)


builder.add_conditional_edges(

    "router",

    choose_node,

    {
        "rag": "rag",
        "emi": "emi",
        "final": "final"
    }

)


builder.add_edge(
    "rag",
    "final"
)

builder.add_edge(
    "emi",
    "final"
)

builder.add_edge(
    "final",
    END
)


graph = builder.compile()