import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Group, Loader, Stack, Text, Title } from "@mantine/core";
import { notifications } from "@mantine/notifications";
import MDEditor from "@uiw/react-md-editor";

import { api } from "@/api/client";
import type { Task } from "@/types";

export default function SpecsModule({ task }: { task: Task }) {
  const qc = useQueryClient();
  const specQ = useQuery({
    queryKey: ["artifact", task.id, "spec"],
    queryFn: () => api.getArtifact(task.id, "spec"),
  });
  const [draft, setDraft] = useState<string>("");
  const [mode, setMode] = useState<"preview" | "edit" | "live">("preview");

  useEffect(() => {
    if (specQ.data?.content !== undefined) setDraft(specQ.data.content ?? "");
  }, [specQ.data]);

  const saveM = useMutation({
    mutationFn: () => api.putArtifact(task.id, "spec", draft, specQ.data?.sha256 ?? undefined),
    onSuccess: () => {
      notifications.show({ title: "Spec saved", message: "spec.md updated.", color: "teal" });
      qc.invalidateQueries({ queryKey: ["artifact", task.id, "spec"] });
    },
    onError: (err) => {
      notifications.show({ title: "Save failed", message: String(err), color: "red" });
    },
  });

  if (specQ.isLoading) return <Loader />;
  const exists = specQ.data?.exists ?? false;

  return (
    <Stack gap="md">
      <Group justify="space-between" align="flex-end">
        <Stack gap={2}>
          <Title order={3}>Spec</Title>
          <Text size="sm" c="dimmed" ff="monospace">specs/specs/{task.id}/spec.md</Text>
        </Stack>
        <Group gap="xs">
          <Button.Group>
            <Button variant={mode === "preview" ? "filled" : "default"} size="xs" onClick={() => setMode("preview")}>Preview</Button>
            <Button variant={mode === "live" ? "filled" : "default"} size="xs" onClick={() => setMode("live")}>Split</Button>
            <Button variant={mode === "edit" ? "filled" : "default"} size="xs" onClick={() => setMode("edit")}>Edit</Button>
          </Button.Group>
          <Button onClick={() => saveM.mutate()} loading={saveM.isPending} disabled={draft === (specQ.data?.content ?? "")}>
            Save
          </Button>
        </Group>
      </Group>
      {!exists && <Text c="dimmed" fs="italic">No spec yet. Run the spec phase via /agent_team.</Text>}
      <div data-color-mode="light">
        <MDEditor
          value={draft}
          onChange={(v) => setDraft(v ?? "")}
          preview={mode}
          height={640}
        />
      </div>
    </Stack>
  );
}
