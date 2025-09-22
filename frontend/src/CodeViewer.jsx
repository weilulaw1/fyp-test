import React, { useEffect, useState } from "react";

const CodeViewer = ({ file }) => {
  const [code, setCode] = useState("");

    useEffect(()=>{
        if (file){
            const normalisedFile = file.replace(/\\/g, "/");
            fetch(`http://localhost:8000/api/files/${encodeURIComponent(normalisedFile)}/`)
                .then((res) => res.text())
                .then((text) => setCode(text))
                .catch((err) => console.error("Failed to load file:", err));
            }else{
                setCode(""); //resets if no file is selected
            }
        }, [file]);

return (
    <div className="p-4">
      {!file ? (
        <div>Select a file from the sidebar</div>
      ) : (
        <>
          <h2 className="text-xl font-bold mb-2">Code Viewer</h2>
            <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="flex-1 w-full font-mono text-lg border border-gray-300 rounded p-4 resize-none overflow-auto"
            style={{ minHeight: 600, minWidth:600 ,whiteSpace: "pre" }}
            />
        </>
      )}
    </div>
  );
};

export default CodeViewer;