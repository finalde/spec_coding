import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Editor } from "@monaco-editor/react";
import { Button, Group, Loader, Stack, Text, Title } from "@mantine/core";
import { notifications } from "@mantine/notifications";

import { api } from "@/api/client";
import type { Task } from "@/types";
import { ensureMonacoConfigured } from "@/editor/monaco_setup";

ensureMonacoConfigured();

export default function ExecutionPlanModule({ task }: { task: Task }) {
  const qc = useQueryClient();
  const planQ = useQuery({
    queryKey: ["artifact", task.id, "plan"],
    queryFn: () => api.getArtifact(task.id, "plan"),
  });
  const [draft, setDraft] = useState<string>("");

  useEffect(() => {
    if (planQ.data?.content !== undefined) setDraft(planQ.data.content ?? "");
  }, [planQ.data]);

  const saveM = useMutation({
    mutationFn: () => api.putArtifact(task.id, "plan", draft, planQ.data?.sha256 ?? undefined),
    onSuccess: () => {
      notifications.show({ title: "Plan saved", message: "plan.yaml updated.", color: "teal" });
      qc.invalidateQueries({ queryKey: ["artifact", task.id, "plan"] });
    },
    onError: (err) => {
      notifications.show({ title: "Save failed", message: String(err), color: "red" });
    },
  });

  if (planQ.isLoading) return <Loader />;
  const exists = planQ.data?.exists ?? false;

  return (
    <Stack gap="md">
      <Group justify="space-between" align="flex-end">
        <Stack gap={2}>
          <Title order={3}>Execution Plan</Title>
          <Text size="sm" c="dimmed" ff="monospace">specs/execution_plans/{task.id}/plan.yaml</Text>
        </Stack>
        <Button
          onClick={() => saveM.mutate()}
          loading={saveM.isPending}
          disabled={draft === (planQ.data?.content ?? "")}
        >
          Save
        </Button>
      </Group>
      {!exists && (
        <Text c="dimmed" fs="italic">No plan yet. Run the plan phase via /agent_team.</Text>
      )}
      <div style={{ border: "1px solid var(--mantine-color-gray-3)", borderRadius: 6 }}>
        <Editor
          height="640px"
          defaultLanguage="yaml"
          value={draft}
          onChange={(v) => setDraft(v ?? "")}
          path="plan.yaml"
          options={{
            minimap: { enabled: false },
            tabSize: 2,
            wordWrap: "on",
            fontSize: 13,
          }}
        />
      </div>
    </Stack>
  );
}
