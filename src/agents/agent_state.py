from typing import TypedDict


class AgentState(TypedDict):
    question: str
    history: list[str]
    pending_action: str
    final_answer: str