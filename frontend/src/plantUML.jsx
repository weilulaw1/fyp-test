import React, {useState}  from "react";
import plantumlEncoder from "plantuml-encoder";


export default function PlantUMLViewer() {
    const [uml, setUml] = useState(
    `@startuml
    Alice -> Bob : Hello
    @enduml`
    );
    const encoded = plantumlEncoder.encode(uml);
    const url = `http://localhost:8080/svg/${encoded}`;
    return (
        <div>
          <h2>PlantUML Diagram</h2>
        <textarea
        rows={6}
        cols={40}
        value={uml}
        onChange={(e) => setUml(e.target.value)}
        />
        <div>
          <img src={url} alt="PlantUML Diagram" />
        </div>
        </div>
      );
}