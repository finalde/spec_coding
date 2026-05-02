// Module-scope Monaco + monaco-yaml configuration. Imported from
// PlanEditor.tsx so the heavy Monaco bundle stays inside the lazy chunk.
//
// The two failure modes we guard against (per yaml_editor research):
//  1. self.MonacoEnvironment must be set BEFORE Monaco loads workers.
//  2. loader.config({ monaco }) must use the same Monaco instance that
//     monaco-yaml mutates — otherwise validation silently no-ops.

import { loader } from "@monaco-editor/react";
import * as monaco from "monaco-editor";
import { configureMonacoYaml } from "monaco-yaml";
import EditorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";

import YamlWorker from "./yaml.worker?worker";
import planSchema from "../schemas/plan.schema.json";

declare global {
  interface Window {
    __monacoConfigured?: boolean;
  }
}

export function ensureMonacoConfigured(): void {
  if (typeof window === "undefined") return;
  if (window.__monacoConfigured) return;

  (self as unknown as {
    MonacoEnvironment: { getWorker(_: string, label: string): Worker };
  }).MonacoEnvironment = {
    getWorker(_: string, label: string) {
      if (label === "yaml") return new YamlWorker();
      return new EditorWorker();
    },
  };

  loader.config({ monaco });

  configureMonacoYaml(monaco, {
    enableSchemaRequest: false,
    hover: true,
    completion: true,
    validate: true,
    format: true,
    schemas: [
      {
        uri: "http://spec-coding/plan.schema.json",
        fileMatch: ["plan.yaml", "*.plan.yaml"],
        schema: planSchema as Record<string, unknown>,
      },
    ],
  });

  window.__monacoConfigured = true;
}
