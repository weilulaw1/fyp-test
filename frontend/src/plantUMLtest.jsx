import React, { useState, useEffect } from "react";
import plantumlEncoder from "plantuml-encoder";

export default function PlantUMLTest() {
  const [uml, setUml] = useState("");
  const [url, setUrl] = useState("");

  useEffect(() => {
    // Hardcoded file path in public folder
    fetch("http://localhost:8000/api/uml/untitled.txt/")
    .then((res) => res.text())
      .then((text) => {
        setUml(text);
        const encoded = plantumlEncoder.encode(text);
        setUrl(`http://localhost:8080/svg/${encoded}`);
      })
      .catch((err) => console.error("Failed to load UML file:", err));
  }, []);

  return (
    <div>
      <h2>PlantUML Diagram from File</h2>
      <textarea
        rows={10}
        cols={50}
        value={uml}
        onChange={(e) => {
          const newUml = e.target.value;
          setUml(newUml);
          const encoded = plantumlEncoder.encode(newUml);
          setUrl(`http://localhost:8080/svg/${encoded}`);
        }}
      />
      {url && (
        <div style={{ marginTop: "20px" }}>
          <img src={url} alt="PlantUML Diagram" style={{ maxWidth: "100%" }} />
        </div>
      )}
    </div>
  );
}
