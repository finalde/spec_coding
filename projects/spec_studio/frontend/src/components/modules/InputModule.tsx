import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Badge, Button, Group, Stack, Tabs, Text, Title } from "@mantine/core";
import { modals } from "@mantine/modals";
import { notifications } from "@mantine/notifications";
import MDEditor from "@uiw/react-md-editor";

import { api } from "@/api/client";
import type { InputSource, Task } from "@/types";

const TAB_LABEL: Record<string, string> = {
  claude_md: "CLAUDE.md",
  skill_md: "SKILL.md",
  phase_manager_md: "Phase manager",
  initial_prompt: "Initial prompt",
};

export default function InputModule({ task }: { task: Task }) {
  const qc = useQueryClient();
  const inputsQ = useQuery({
    queryKey: ["inputs", task.id],
    queryFn: () => api.getInputs(task.id),
  });

  const [draft, setDraft] = useState<Record<string, string>>({});
  const [activeTab, setActiveTab] = useState<string>("claude_md");

  useEffect(() => {
    if (inputsQ.data) {
      const next: Record<string, string> = {};
      for (const s of inputsQ.data.sources) next[s.kind] = s.content;
      setDraft(next);
    }
  }, [inputsQ.data]);

  const sources = inputsQ.data?.sources ?? [];
  const current = sources.find((s) => s.kind === activeTab);

  const saveM = useMutation({
    mutationFn: async ({ source, content }: { source: InputSource; content: string }) => {
      if (source.kind === "initial_prompt") {
        return api.putArtifact(task.id, "initial_prompt", content, source.sha256);
      }
      if (source.kind === "claude_md" || source.kind === "skill_md") {
        return api.putInput(source.kind, content, true, source.sha256);
      }
      const agentName = source.path.split(/[\\/]/).pop()?.replace(/\.md$/, "") ?? "";
      return api.putAgent(agentName, content, true, source.sha256);
    },
    onSuccess: (_res, vars) => {
      notifications.show({
        title: "Saved",
        message: `${TAB_LABEL[vars.source.kind] ?? vars.source.kind} written.`,
        color: "teal",
      });
      qc.invalidateQueries({ queryKey: ["inputs", task.id] });
    },
    onError: (err) => {
      notifications.show({
        title: "Save failed",
        message: String(err),
        color: "red",
      });
    },
  });

  function onSave() {
    if (!current) return;
    const content = draft[current.kind] ?? "";
    if (current.requires_confirm) {
      modals.openConfirmModal({
        title: `Save ${TAB_LABEL[current.kind]}?`,
        children: (
          <Text size="sm">
            This file is repo-level — your edit affects every task in this repo, not just{" "}
            <Text span fw={600}>{task.name}</Text>. The previous content will be backed up to{" "}
            <Text span ff="monospace">{current.path}.bak</Text>.
          </Text>
        ),
        labels: { confirm: "Save anyway", cancel: "Cancel" },
        confirmProps: { color: "red" },
        onConfirm: () => saveM.mutate({ source: current, content }),
      });
    } else {
      saveM.mutate({ source: current, content });
    }
  }

  if (!inputsQ.data) {
    return <Text c="dimmed">Loading inputs...</Text>;
  }

  return (
    <Stack gap="md">
      <Stack gap={2}>
        <Title order={3}>Input</Title>
        <Text size="sm" c="dimmed">
          Every input that influences downstream generation. Edits persist only — saving never
          triggers a re-run automatically.
        </Text>
      </Stack>

      <Tabs value={activeTab} onChange={(v) => v && setActiveTab(v)}>
        <Tabs.List>
          {sources.map((s) => (
            <Tabs.Tab
              key={s.kind}
              value={s.kind}
              rightSection={
                s.requires_confirm ? <Badge size="xs" color="orange" variant="light">repo</Badge> : null
              }
            >
              {TAB_LABEL[s.kind] ?? s.kind}
            </Tabs.Tab>
          ))}
        </Tabs.List>
      </Tabs>

      {current && (
        <Stack gap="xs">
          <Group justify="space-between" align="center">
            <Text size="xs" c="dimmed" ff="monospace">{current.path}</Text>
            <Group gap="xs">
              {current.requires_confirm && (
                <Badge color="orange" variant="light">requires confirm</Badge>
              )}
              <Button
                size="xs"
                onClick={onSave}
                loading={saveM.isPending}
                disabled={(draft[current.kind] ?? "") === current.content}
              >
                Save
              </Button>
            </Group>
          </Group>
          <div data-color-mode="light">
            <MDEditor
              value={draft[current.kind] ?? ""}
              onChange={(v) => setDraft((d) => ({ ...d, [current.kind]: v ?? "" }))}
              preview="edit"
              height={520}
            />
          </div>
        </Stack>
      )}
    </Stack>
  );
}
