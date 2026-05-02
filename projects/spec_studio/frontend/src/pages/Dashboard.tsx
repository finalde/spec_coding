import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import type { CreateTaskInput, RootFolder } from "@/types";

export default function Dashboard() {
  const qc = useQueryClient();
  const tasksQ = useQuery({ queryKey: ["tasks"], queryFn: () => api.listTasks() });
  const rootsQ = useQuery({ queryKey: ["roots"], queryFn: () => api.rootFolders() });

  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [rootFolder, setRootFolder] = useState<RootFolder>("projects");
  const [prompt, setPrompt] = useState("");

  const createM = useMutation({
    mutationFn: (input: CreateTaskInput) => api.createTask(input),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["tasks"] });
      setShowForm(false);
      setName("");
      setPrompt("");
    },
  });

  return (
    <div className="max-w-6xl mx-auto px-6 py-6">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold">Tasks</h1>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="bg-slate-900 text-white px-3 py-1.5 rounded text-sm hover:bg-slate-700"
        >
          {showForm ? "Cancel" : "+ New task"}
        </button>
      </div>

      {showForm && (
        <div className="bg-white border rounded-lg p-4 mb-6 space-y-3">
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Name (slug)</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="hello_cli"
              className="w-full border rounded px-2 py-1 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">root_folder</label>
            <select
              value={rootFolder}
              onChange={(e) => setRootFolder(e.target.value as RootFolder)}
              className="w-full border rounded px-2 py-1 text-sm"
            >
              {(rootsQ.data ?? ["projects", "ai_videos"]).map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">Initial prompt</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={4}
              placeholder="Describe what you want to build..."
              className="w-full border rounded px-2 py-1 text-sm font-mono"
            />
          </div>
          <button
            disabled={!name || !prompt || createM.isPending}
            onClick={() => createM.mutate({ name, root_folder: rootFolder, initial_prompt: prompt })}
            className="bg-slate-900 text-white px-3 py-1.5 rounded text-sm disabled:bg-slate-300"
          >
            {createM.isPending ? "Creating..." : "Create"}
          </button>
          {createM.error && <div className="text-red-600 text-xs">{String(createM.error)}</div>}
        </div>
      )}

      <div className="bg-white border rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-100 text-left">
            <tr>
              <th className="px-3 py-2 font-medium">Name</th>
              <th className="px-3 py-2 font-medium">root_folder</th>
              <th className="px-3 py-2 font-medium">Phase</th>
              <th className="px-3 py-2 font-medium">Status</th>
              <th className="px-3 py-2 font-medium">Updated</th>
            </tr>
          </thead>
          <tbody>
            {tasksQ.isLoading && (
              <tr><td colSpan={5} className="px-3 py-6 text-center text-slate-400">Loading...</td></tr>
            )}
            {tasksQ.data?.length === 0 && (
              <tr><td colSpan={5} className="px-3 py-6 text-center text-slate-400">No tasks yet.</td></tr>
            )}
            {tasksQ.data?.map((t) => (
              <tr key={t.id} className="border-t hover:bg-slate-50">
                <td className="px-3 py-2">
                  <Link to={`/tasks/${t.id}`} className="text-blue-600 hover:underline">{t.name}</Link>
                  <div className="text-xs text-slate-400 font-mono">{t.id}</div>
                </td>
                <td className="px-3 py-2"><span className="text-xs px-2 py-0.5 rounded bg-slate-200">{t.root_folder}</span></td>
                <td className="px-3 py-2">{t.current_phase}</td>
                <td className="px-3 py-2">{t.status}</td>
                <td className="px-3 py-2 text-xs text-slate-500">{t.updated_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
