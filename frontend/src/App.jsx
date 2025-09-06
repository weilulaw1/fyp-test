import './App.css'
import { useEffect } from "react";
import MenuBar from './MenuBar';

function App() {
  useEffect(() => {
    const menus = document.querySelectorAll("[class*='dropdown']");
    document.querySelectorAll("div[style*='fontWeight: bold']").forEach((menuLabel, idx) => {
      menuLabel.addEventListener("mouseenter", () => {
        menus[idx].style.display = "block";
      });
      menuLabel.parentElement.addEventListener("mouseleave", () => {
        menus[idx].style.display = "none";
      });
    });
  }, []);

  return (
    <div>
      <MenuBar />
      <div style={{ padding: "20px" }}>
        <h1>Home Page</h1>
      </div>
    </div>
  );
}
export default App;