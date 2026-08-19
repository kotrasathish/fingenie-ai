import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
)
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0.7)

chat_history = [
    SystemMessage(content="You are a helpful assistant.")]

def chat(user_input: str) -> str:
    chat_history.append(HumanMessage(content=user_input))

    response = llm.invoke(chat_history)

    print("Response:", response)
    print("Content:", response.content)
    print("Type:", type(response.content))

    # Handle new LangChain/Gemini response format
    if isinstance(response.content, list):
        reply = ""

        for item in response.content:
            if isinstance(item, dict) and item.get("type") == "text":
                reply += item.get("text", "")

        if not reply:
            reply = str(response.content)
    else:
        reply = str(response.content)

    chat_history.append(AIMessage(content=reply))

    return reply