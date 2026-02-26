import React, { useState, useEffect } from "react";

const PlantUMLTestSVG = ({ file }) => {
  const [svgContent, setSvgContent] = useState("");

  const fetchSvg = async (umlText) => {
    try {
      const res = await fetch("http://localhost:8080/svg", {
        method: "POST",
        headers: { "Content-Type": "text/plain; charset=utf-8" },
        body: umlText,
      });

      const text = await res.text();
      setSvgContent(text);
    } catch (err) {
      console.error("Failed to load SVG:", err);
    }
  };

  useEffect(() => {
    if (!file) return;

    const normalisedFile = file.replace(/\\/g, "/");

    fetch(`http://localhost:8000/api/files/${encodeURIComponent(normalisedFile)}/`)
      .then((res) => res.text())
      .then((text) => {
        fetchSvg(text);
      })
      .catch((err) => console.error("Failed to load UML file:", err));
  }, [file]);

  return (
    <div
      style={{
        width: "100%",
        height: "85vh",
        overflow: "auto",
        border: "1px solid #ddd",
        background: "white",
      }}
      dangerouslySetInnerHTML={{ __html: svgContent }}
    />
  );
};

export default PlantUMLTestSVG;
