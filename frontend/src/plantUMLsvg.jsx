import React, { useState, useEffect } from "react";
import plantumlEncoder from "plantuml-encoder";

export default function PlantUMLTestSVG() {
  const [uml, setUml] = useState("");
  const [svgContent, setSvgContent] = useState("");

  const fetchSvg = (umlText) => {
    const encoded = plantumlEncoder.encode(umlText);
    fetch(`http://localhost:8080/svg/${encoded}`)
      .then((res) => res.text())
      .then(setSvgContent)
      .catch((err) => console.error("Failed to load SVG:", err));
  };

  useEffect(() => {
    // Fetch UML text from backend or public folder
    fetch("http://localhost:8000/api/uml/untitled.txt/")
      .then((res) => res.text())
      .then((text) => {
        setUml(text);
        fetchSvg(text);
      })
      .catch((err) => console.error("Failed to load UML file:", err));
  }, []);

  return (
    <div>
      <h2>PlantUML Diagram (SVG)</h2>
      <textarea
        rows={10}
        cols={50}
        value={uml}
        onChange={(e) => {
          const newUml = e.target.value;
          setUml(newUml);
          fetchSvg(newUml);
        }}
      />

      <div
        style={{ marginTop: "20px", marginLeft:"-200px" }}
        // Inject SVG directly into DOM
        dangerouslySetInnerHTML={{ __html: svgContent }}
      />
    </div>
  );
}
