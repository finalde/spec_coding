---
name: meeting-assistant
description: Use this skill whenever the user mentions meetings, agendas, meeting notes, action items, follow-ups, summaries of discussions, or preparing for a call. This includes requests like "help me prep for my standup", "summarize this meeting", "write up action items", "create an agenda", or "draft a follow-up email". Activate proactively even when the user doesn't say the word "meeting" but the context clearly involves team coordination, calls, or recorded discussions.
version: 1.0.0
---

# Meeting Assistant

Help users get the most out of their meetings — before, during, and after.

## What This Skill Covers

- **Pre-meeting**: Agenda creation, prep notes, talking points
- **During**: Structured note-taking templates
- **Post-meeting**: Summaries, action items, follow-up drafts

Identify where in the meeting lifecycle the user is and jump to the relevant section below.

---

## Pre-Meeting: Agenda & Preparation

When the user wants to prepare for an upcoming meeting, ask for (or infer from context):
- Meeting purpose and type (standup, retrospective, 1:1, planning, review, etc.)
- Attendees and their roles
- Duration
- Any existing notes or background

### Agenda format

Use this structure unless the user requests otherwise:

```
## [Meeting Title]
**Date/Time**: ...
**Attendees**: ...
**Duration**: ...

### Objectives
- What we need to decide or accomplish

### Agenda
1. [Topic] — [owner] — [time]
2. ...

### Pre-read / Background
- ...

### Parking Lot (topics to defer if short on time)
- ...
```

Keep agenda items timeboxed and ordered by priority. Put "must decide" items first — don't let them get crowded out by updates.

---

## During: Note-Taking Template

When the user wants a template for taking notes in an active meeting:

```
## [Meeting Title] — [Date]
**Attendees**: ...

### Key Decisions
-

### Discussion Notes
-

### Action Items
| Item | Owner | Due Date |
|------|-------|----------|
|      |       |          |

### Follow-up / Next Meeting
-
```

Keep notes factual and brief. Capture decisions and actions, not a transcript.

---

## Post-Meeting: Summary & Action Items

When the user provides raw notes, a transcript, or a rough dump of what happened, produce:

1. **Executive summary** (2–4 sentences): what was discussed and decided
2. **Key decisions**: bulleted list of decisions made
3. **Action items**: table with item, owner, and due date
4. **Open questions / Parking lot**: items not resolved
5. **Follow-up email draft** (if requested)

### Extracting action items

Look for language like:
- "[Name] will ...", "Let's have [name] ..."
- "We need to ...", "Someone should ..."
- "By [date]", "Before next [meeting]"

If ownership or due date is missing, flag it rather than guessing.

### Follow-up email format

```
Subject: [Meeting name] — Summary & Next Steps ([Date])

Hi [names / team],

Thanks for joining today. Here's a quick recap:

**Decisions made:**
- ...

**Action items:**
- [ ] [Item] — [Owner] — due [date]

**Next meeting:** [date/time or TBD]

Let me know if I missed anything.

[Name]
```

---

## Tips for Good Output

- Match the user's register: casual for standups, formal for exec reviews
- Ask clarifying questions if the input is ambiguous — don't invent context
- If given a long transcript, skim for decisions and action verbs; don't summarize every exchange
- Prefer bullet points over paragraphs for scannability
- Always surface unresolved questions explicitly — they're easy to lose track of

