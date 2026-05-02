import { Link, Navigate, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import TaskDetail from "./pages/TaskDetail";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b bg-white">
        <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
          <Link to="/" className="text-lg font-semibold tracking-tight">
            spec_studio
          </Link>
          <span className="text-xs text-slate-500">single-user · 127.0.0.1</span>
        </div>
      </header>
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/tasks/:taskId" element={<Navigate to="input" replace />} />
          <Route path="/tasks/:taskId/:module" element={<TaskDetail />} />
        </Routes>
      </main>
    </div>
  );
}
