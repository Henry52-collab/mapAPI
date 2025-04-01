from map import Map
from ans import ANS
#import drive
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Node, Edge

#Creates the FastAPI application instance.
app = FastAPI()
#Lets the frontend make requests to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Build Map
map = Map("locations.csv", "routes.csv")

#GET /map endpoint
@app.get("/map")
def get_map():
    #iterates through all nodes in the graph and builds a dictionary with just their names and coordinates
    nodes = {
        node: {
            "x": data.get("x"),
            "y": data.get("y")
        }
        for node, data in map._G.nodes(data=True)
    }
    #iterates through all edges in the graph and builds a dictionary
    edges = [
        {
            "from_node": u,
            "to_node": v,
            "route_name": data.get("route_name"),
            "time": data.get("time"),
            "safety": data.get("safety"),
            "eco": data.get("eco")
        }
        for u, v, data in map._G.edges(data=True)
    ]

    #return the data to the frontend as a JSON response
    return {"nodes": nodes, "edges": edges}

# Get turn sequence
attributr_weights = {"distance":1,"speed":1,"traffic":1}
ans = ANS(map,attributr_weights)
turns = ans.get_turn_sequence("R2",(38,10))

@app.post("/update-node/{node_id}")
def update_node(node_id: str, node: Node):
    if node_id not in map._G.nodes:
        raise HTTPException(status_code=404, detail="Node not found")
    map.add_location(node_id, x=node.x, y=node.y)
    return {"message": f"Updated node {node_id}"}

#POST /update-edge endpoint
@app.post("/update-edge")
def update_edge(edge: Edge):
    #check if the edge exist
    if not map._G.has_edge(edge.from_node, edge.to_node):
        raise HTTPException(status_code=404, detail="Edge not found")
    #update the edge with new weights
    map.add_route(
        edge.from_node,
        edge.to_node,
        time=edge.time,
        safety=edge.safety,
        eco=edge.eco
    )
    return {"message": f"Updated edge {edge.from_node} → {edge.to_node}"}
    


# Excecute
#drive.drive(turns)



