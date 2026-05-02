import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Button, Group, Loader, Stack, Text, Title } from "@mantine/core";
import { notifications } from "@mantine/notifications";

import { api } from "@/api/client";
import type { InterviewQA, InterviewQuestion, Task } from "@/types";
import InterviewQuestionCard from "./InterviewQuestionCard";

export default function InterviewModule({ task }: { task: Task }) {
  const qc = useQueryClient();
  const qaQ = useQuery({
    queryKey: ["interview", task.id],
    queryFn: () => api.getInterview(task.id),
  });

  const [draft, setDraft] = useState<InterviewQA | null>(null);

  useEffect(() => {
    if (qaQ.data) setDraft(qaQ.data);
  }, [qaQ.data]);

  const saveM = useMutation({
    mutationFn: () => api.putInterview(task.id, draft as InterviewQA),
    onSuccess: () => {
      notifications.show({
        title: "Interview saved",
        message: "qa.md re-rendered. Spec recompile is manual.",
        color: "teal",
      });
      qc.invalidateQueries({ queryKey: ["interview", task.id] });
    },
    onError: (err) => {
      notifications.show({ title: "Save failed", message: String(err), color: "red" });
    },
  });

  if (qaQ.isLoading || !draft) return <Loader />;
  if (qaQ.error) {
    return <Text c="red">Failed to load interview: {String(qaQ.error)}</Text>;
  }

  function updateQuestion(roundIdx: number, qIdx: number, next: InterviewQuestion) {
    if (!draft) return;
    const rounds = draft.rounds.map((r, ri) =>
      ri !== roundIdx
        ? r
        : { ...r, questions: r.questions.map((q, qi) => (qi !== qIdx ? q : next)) },
    );
    setDraft({ ...draft, rounds });
  }

  return (
    <Stack gap="md">
      <Group justify="space-between" align="flex-end">
        <Stack gap={2}>
          <Title order={3}>Interview Questions</Title>
          <Text size="sm" c="dimmed">
            Multi-turn choice-based Q&amp;A. Edits persist to{" "}
            <Text span ff="monospace" size="sm">specs/interviews/{task.id}/qa.md</Text>; downstream
            artifacts are not regenerated automatically.
          </Text>
        </Stack>
        <Button onClick={() => saveM.mutate()} loading={saveM.isPending}>
          Save
        </Button>
      </Group>

      {draft.rounds.length === 0 && (
        <Text c="dimmed" fs="italic">
          No interview rounds yet. Run the interview phase via{" "}
          <Text span ff="monospace" size="sm">/agent_team</Text> in Claude Code.
        </Text>
      )}

      {draft.rounds.map((round, ri) => (
        <Stack key={round.number} gap="sm">
          <Title order={5}>Round {round.number}</Title>
          {round.questions.map((q, qi) => (
            <InterviewQuestionCard
              key={q.qid}
              question={q}
              onChange={(next) => updateQuestion(ri, qi, next)}
            />
          ))}
        </Stack>
      ))}

      {draft.open_questions.length > 0 && (
        <Stack gap={4}>
          <Title order={5}>Open Questions</Title>
          {draft.open_questions.map((oq, i) => (
            <Text key={i} size="sm">• {oq}</Text>
          ))}
        </Stack>
      )}
    </Stack>
  );
}
