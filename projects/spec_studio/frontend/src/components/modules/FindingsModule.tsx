import { useQuery } from "@tanstack/react-query";
import { Loader, Stack, Text, Title } from "@mantine/core";
import MDEditor from "@uiw/react-md-editor";

import { api } from "@/api/client";
import type { Task } from "@/types";

export default function FindingsModule({ task }: { task: Task }) {
  const dossierQ = useQuery({
    queryKey: ["artifact", task.id, "dossier"],
    queryFn: () => api.getArtifact(task.id, "dossier"),
  });

  if (dossierQ.isLoading) return <Loader />;
  const exists = dossierQ.data?.exists ?? false;

  return (
    <Stack gap="md">
      <Stack gap={2}>
        <Title order={3}>Findings</Title>
        <Text size="sm" c="dimmed" ff="monospace">specs/findings/{task.id}/dossier.md</Text>
      </Stack>
      {!exists ? (
        <Text c="dimmed" fs="italic">No dossier yet. Run the research phase via /agent_team.</Text>
      ) : (
        <div data-color-mode="light">
          <MDEditor.Markdown source={dossierQ.data?.content ?? ""} />
        </div>
      )}
      <Text size="xs" c="dimmed" fs="italic">
        Per-angle findings live alongside the dossier under{" "}
        <Text span ff="monospace" size="xs">specs/findings/{task.id}/</Text>. View them via the
        files browser; per-angle accordion in this UI is a v2 follow-up.
      </Text>
    </Stack>
  );
}
