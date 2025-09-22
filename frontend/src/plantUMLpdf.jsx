import React, { useState, useEffect } from "react";
import plantumlEncoder from "plantuml-encoder";

export default function PlantUMLpdfTest() {
  const [uml, setUml] = useState("");
  const [pdfUrl, setPdfUrl] = useState("");

  const fetchPdf = (umlText) => {
    const encoded = plantumlEncoder.encode(umlText);
    const url = `http://localhost:8080/pdf/${encoded}`;
    setPdfUrl(url); // point directly to PlantUML server's PDF output
  };

  useEffect(() => {
    // Load UML text from backend or file
    fetch("http://localhost:8000/api/uml/untitled.txt/")
      .then((res) => res.text())
      .then((text) => {
        setUml(text);
        fetchPdf(text);
      })
      .catch((err) => console.error("Failed to load UML file:", err));
  }, []);

  return (
    <div>
      <h2>PlantUML Diagram (PDF Viewer)</h2>

      <textarea
        rows={10}
        cols={50}
        value={uml}
        onChange={(e) => {
          const newUml = e.target.value;
          setUml(newUml);
          fetchPdf(newUml);
        }}
      />

      <div style={{ marginTop: "20px", height: "600px", width: "100%" }}>
        {pdfUrl && (
          <object
            data={pdfUrl}
            type="application/pdf"
            width="200%"
            height="100%"
          >
            <p>
              PDF cannot be displayed.{" "}
              <a href={pdfUrl} target="_blank" rel="noopener noreferrer">
                Download PDF
              </a>
            </p>
          </object>
        )}
      </div>
    </div>
  );
}
