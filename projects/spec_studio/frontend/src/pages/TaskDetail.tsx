import { lazy, Suspense } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  AppShell,
  Badge,
  Box,
  Group,
  Loader,
  NavLink,
  Stack,
  Text,
  Title,
} from "@mantine/core";

import { api } from "@/api/client";
import type { ModuleKey } from "@/types";
import InputModule from "@/components/modules/InputModule";
import InterviewModule from "@/components/modules/InterviewModule";
import SpecsModule from "@/components/modules/SpecsModule";
import FindingsModule from "@/components/modules/FindingsModule";

const ExecutionPlanModule = lazy(
  () => import("@/components/modules/ExecutionPlanModule"),
);

const MODULES: { key: ModuleKey; label: string }[] = [
  { key: "input", label: "Input" },
  { key: "interview", label: "Interview Questions" },
  { key: "specs", label: "Specs" },
  { key: "findings", label: "Findings" },
  { key: "plan", label: "Execution Plan" },
];

const VALID_MODULES = new Set<ModuleKey>(MODULES.map((m) => m.key));

export default function TaskDetail() {
  const { taskId = "", module: moduleParam = "input" } = useParams<{
    taskId: string;
    module: string;
  }>();
  const navigate = useNavigate();
  const taskQ = useQuery({
    queryKey: ["task", taskId],
    queryFn: () => api.getTask(taskId),
    enabled: !!taskId,
  });

  if (!taskQ.data) {
    return (
      <Box p="xl">
        <Text c="dimmed">{taskQ.isLoading ? "Loading task..." : "Task not found."}</Text>
      </Box>
    );
  }
  const task = taskQ.data;
  const active: ModuleKey = (
    VALID_MODULES.has(moduleParam as ModuleKey) ? moduleParam : "input"
  ) as ModuleKey;

  return (
    <AppShell
      navbar={{ width: 260, breakpoint: 0 }}
      padding="md"
      withBorder={false}
    >
      <AppShell.Navbar p="md" withBorder>
        <Stack gap="sm">
          <Stack gap={2}>
            <Title order={4} style={{ wordBreak: "break-word" }}>
              {task.name}
            </Title>
            <Text size="xs" c="dimmed" style={{ fontFamily: "ui-monospace, monospace" }}>
              {task.id}
            </Text>
          </Stack>
          <Group gap="xs">
            <Badge variant="light" color="gray" size="sm">{task.root_folder}</Badge>
            <Badge variant="dot" color="blue" size="sm">{task.current_phase}</Badge>
            <Badge variant="outline" color="gray" size="sm">{task.status}</Badge>
          </Group>
          <Stack gap={4} mt="md">
            {MODULES.map((m) => (
              <NavLink
                key={m.key}
                label={m.label}
                active={active === m.key}
                variant="filled"
                onClick={() => navigate(`/tasks/${taskId}/${m.key}`)}
              />
            ))}
          </Stack>
        </Stack>
      </AppShell.Navbar>
      <AppShell.Main>
        <Box maw={1100} mx="auto">
          {active === "input" && <InputModule task={task} />}
          {active === "interview" && <InterviewModule task={task} />}
          {active === "specs" && <SpecsModule task={task} />}
          {active === "findings" && <FindingsModule task={task} />}
          {active === "plan" && (
            <Suspense fallback={<Loader />}>
              <ExecutionPlanModule task={task} />
            </Suspense>
          )}
        </Box>
      </AppShell.Main>
    </AppShell>
  );
}
