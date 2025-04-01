from pydantic import BaseModel

class Node(BaseModel):
    x: float
    y: float

class Edge(BaseModel):
    from_node: str
    to_node: str
    time: float
    safety: float
    eco: float
