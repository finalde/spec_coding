import { Badge, Card, Chip, Group, Stack, Text, Textarea } from "@mantine/core";
import type { InterviewQuestion } from "@/types";

const PERSPECTIVE_COLORS: Record<string, string> = {
  Goal: "indigo",
  Scope: "blue",
  Users: "cyan",
  "Tech constraints": "teal",
  Quality: "green",
  "Edge cases": "orange",
  "Edge cases / risks": "orange",
  "Prior art": "violet",
  "Origin / runtime": "pink",
  "Scope — module set": "blue",
  "Scope — editing semantics": "grape",
};

function colorFor(perspective: string): string {
  if (PERSPECTIVE_COLORS[perspective]) return PERSPECTIVE_COLORS[perspective];
  for (const key of Object.keys(PERSPECTIVE_COLORS)) {
    if (perspective.startsWith(key)) return PERSPECTIVE_COLORS[key];
  }
  return "gray";
}

interface Props {
  question: InterviewQuestion;
  onChange: (next: InterviewQuestion) => void;
}

export default function InterviewQuestionCard({ question, onChange }: Props) {
  const pickedKeys = question.options.filter((o) => o.picked).map((o) => o.key);
  const multi = question.kind === "multi" || pickedKeys.length > 1;

  function togglePick(key: string) {
    const next = {
      ...question,
      options: question.options.map((o) =>
        o.key === key ? { ...o, picked: !o.picked } : multi ? o : { ...o, picked: false },
      ),
    };
    onChange(next);
  }

  return (
    <Card withBorder padding="md" radius="md" shadow="xs">
      <Stack gap="sm">
        <Group gap="sm" align="center">
          <Badge color={colorFor(question.perspective)} variant="light">
            {question.perspective || "—"}
          </Badge>
          <Text size="xs" c="dimmed" ff="monospace">{question.qid}</Text>
        </Group>
        <Text fw={600}>{question.text}</Text>
        <Group gap="xs">
          {question.options.map((opt) => (
            <Chip
              key={opt.key}
              checked={opt.picked}
              onChange={() => togglePick(opt.key)}
              variant={opt.picked ? "filled" : "outline"}
              color={colorFor(question.perspective)}
            >
              <Text component="span" fw={600} mr={6}>{opt.key})</Text>
              {opt.text}
            </Chip>
          ))}
        </Group>
        <Textarea
          label="Notes"
          placeholder="Free-text rationale, override, or 'Other:' answer"
          value={question.notes ?? ""}
          onChange={(e) => onChange({ ...question, notes: e.currentTarget.value || null })}
          autosize
          minRows={1}
          maxRows={6}
        />
      </Stack>
    </Card>
  );
}
