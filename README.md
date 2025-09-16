 fyp-test


git add frontend myapp myproject

git commit -m "update to app"

git push origin main



plant uml : 

npm install plantuml-encoder

1) user writes PlantUML test (eg in a text area)
@startuml
Alice -> Bob : Hello
@enduml

2) encode using plantUML's compression algorithm : https://www.npmjs.com/package/plantuml-encoder

  const encoded = plantumlEncoder.encode(uml);
  const url = `http://localhost:8080/svg/${encoded}`;

3) display in frontend or fetch png and render directly