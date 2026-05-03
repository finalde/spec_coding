import { Routes, Route } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";
import { Reader } from "./components/Reader";
import { ProjectPage } from "./components/ProjectPage";
import { Home } from "./components/Home";

export function App() {
  return (
    <div className="app">
      <Sidebar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/file/*" element={<Reader />} />
        <Route path="/project/:type/:name" element={<ProjectPage />} />
      </Routes>
    </div>
  );
}
