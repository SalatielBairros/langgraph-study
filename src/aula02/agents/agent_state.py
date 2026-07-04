from typing import TypedDict, Annotated
import operator
from langchain.messages import AnyMessage

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]