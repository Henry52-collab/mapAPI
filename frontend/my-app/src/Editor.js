import React, { useEffect, useState } from "react";
import "./Editor.css";
const Editor = () => {
  const [mapData, setMapData] = useState(null);

  const [nodeId, setNodeId] = useState("");
  const [x, setX] = useState(0);
  const [y, setY] = useState(0);

  const [edgeFrom, setEdgeFrom] = useState("");
  const [edgeTo, setEdgeTo] = useState("");

  const [time, setTime] = useState(50);
  const [safety, setSafety] = useState(50);
  const [eco, setEco] = useState(50);

  // Fetch the map from the backend
  useEffect(() => {
    fetch("http://localhost:8000/map")
      .then((res) => res.json())
      .then((data) => {
        setMapData(data);
        const nodeNames = Object.keys(data.nodes);
        if (nodeNames.length > 0) {
          setNodeId(nodeNames[0]);
          setEdgeFrom(nodeNames[0]);
          setEdgeTo(nodeNames[1] || nodeNames[0]);
        }
      });
  }, []);

  const updateNode = async () => {
    await fetch(`http://localhost:8000/update-node/${nodeId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ x: parseFloat(x), y: parseFloat(y) }),
    });
    alert("Node updated!");
  };

  const updateEdge = async () => {
    await fetch("http://localhost:8000/update-edge", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        from_node: edgeFrom,
        to_node: edgeTo,
        time: parseFloat(time),
        safety: parseFloat(safety),
        eco: parseFloat(eco),
      }),
    });
    alert("Edge updated!");
  };

  return (
    // dropdown
    <div style={{ padding: 40, top:-50}} class="form">
        <h2>Update Node Coordinates</h2>
        <label class="btn-shine">Select Node: </label>
        <div>
        <select value={nodeId} onChange={(e) => setNodeId(e.target.value)}>
          {mapData &&
            Object.keys(mapData.nodes).map((node) => (
              <option key={node} value={node}>
                {node}
              </option>
            ))}
        </select>
    </div>

      <br />
      {/* x field */}
      <div class = "form">
        <input
          type="number"
          class = "input"
          placeholder="X coordinate"
          value={x}
          onChange={(e) => setX(e.target.value)}
        />
        <span class="input-border"></span>
      </div>
      {/* y field */}
      <div class = "form">
        <input
          type="number"
          class = "input"
          placeholder="Y coordinate"
          value={y}
          onChange={(e) => setY(e.target.value)}
        />
        <span class="input-border"></span>
      </div>

      <button onClick={updateNode}>Update Node</button>

      <h2>Update Edge Weights</h2>
      <label>From: </label>
      <select value={edgeFrom} onChange={(e) => setEdgeFrom(e.target.value)}>
        {mapData &&
          Object.keys(mapData.nodes).map((node) => (
            <option key={node} value={node}>
              {node}
            </option>
          ))}
      </select>

      <label > To: </label>
      <select value={edgeTo} onChange={(e) => setEdgeTo(e.target.value)}>
        {mapData &&
          Object.keys(mapData.nodes).map((node) => (
            <option key={node} value={node}>
              {node}
            </option>
          ))}
      </select>

      <div>
        <label class="btn-shine">Time: {time}</label>
        <input
          class="slider"
          type="range"
          min="0"
          max="100"
          value={time}
          onChange={(e) => setTime(e.target.value)}
        />
      </div>
      <div>
        <label class="btn-shine">Safety: {safety}</label>
        <input
          class="slider"
          type="range"
          min="0"
          max="100"
          value={safety}
          onChange={(e) => setSafety(e.target.value)}
        />
      </div>
      <div>
        <label class="btn-shine">Eco: {eco}</label>
        <input
          class="slider"
          type="range"
          min="0"
          max="100"
          value={eco}
          onChange={(e) => setEco(e.target.value)}
        />
      </div>
      <button onClick={updateEdge}>Update Edge</button>
    </div>
  );
};

export default Editor;
