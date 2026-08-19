from typing import TypedDict, Optional, List, Dict


class AgentState(TypedDict, total=False):

    message: str

    intent: str

    context: str

    result: str

    reply: str

    sources: List[Dict]

    conversation_id: Optional[int]