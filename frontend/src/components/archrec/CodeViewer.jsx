import React, { useEffect, useState } from "react";

const CodeViewer = ({ file, rootKey = "media" }) => {
  const [code, setCode] = useState("");

  useEffect(() => {
    if (!file) {
      setCode("");
      return;
    }

    const normalisedFile = file.replace(/\\/g, "/");

    //  include root key so backend resolves against correct root
    const url = `http://localhost:8000/api/files/${encodeURIComponent(
      normalisedFile
    )}/?root=${encodeURIComponent(rootKey)}`;

    fetch(url)
      .then(async (res) => {
        const text = await res.text();
        if (!res.ok) {
          // Surface backend errors in the viewer (403/404 etc.)
          throw new Error(text || `HTTP ${res.status}`);
        }
        return text;
      })
      .then((text) => setCode(text))
      .catch((err) => {
        console.error("Failed to load file:", err);
        setCode(`Failed to load file:\n${err.message}\n\nURL:\n${url}`);
      });
  }, [file, rootKey]);

  return (
    <div className="p-4">
      {!file ? (
        <div>Select a file from the sidebar</div>
      ) : (
        <>
          <h2 className="text-xl font-bold mb-2">
            Code Viewer{" "}
            <span style={{ fontSize: 12, opacity: 0.7 }}>
              ({rootKey}: {file})
            </span>
          </h2>

          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="flex-1 w-full font-mono text-lg border border-gray-300 rounded p-4 resize-none overflow-auto"
            style={{ minHeight: 600, minWidth: 600, whiteSpace: "pre" }}
          />
        </>
      )}
    </div>
  );
};

export default CodeViewer;