from typing import TypedDict


class AgentState(TypedDict):
    question: str
    messages: list[str]
    pending_action: str
    final_answer: str