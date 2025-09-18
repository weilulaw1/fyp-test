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



todo:

open specific uml.txt from within backend
integrate arch rev with backend
decide on how the uml.txt will be saved: in main "MEDIA" folder or within the uploaded folders for arch rec
possibly afew tabs 3-5 to allow for multiple arch rec folders to display uml diagram at the same time

allow saving of diagram
renaming of tabs

(if possible) link pdf or svg version to the files to be opened when click upon on

deletion of files from frontend?

undo redo function?

open renamed to upload folder, open to be used to actually open uml.txt

possibility of getting folder from github
