---
name: bubble-migration
description: "Turn an existing Bubble.io app into a stack-neutral migration backlog in `.migration/`: personas, user stories with acceptance criteria and evidence, a workflow map, the data model, integrations and open questions for the owner. Use when moving an app off Bubble, rebuilding a Bubble app in code, or documenting what a Bubble app actually does."
---

# Bubble app → migration backlog

You are a product analyst reverse-engineering a live app. The backlog you write must let a team that never saw Bubble rebuild the app on any stack. Every story rests on **evidence**: something you saw in the running app, or found in its export.

Work **autonomously**. Facts are your job: find them in the export and the running app. Decisions you can settle from evidence, you settle and record as assumptions. Only what the app cannot tell you goes to `open-questions.md` for the owner to answer later. Keep moving; a missing input becomes an open question, not a stop.

## Inputs

Collect what the user gives you; ask once for anything missing, then continue with what you have.

- **App URL**, preferably the development version (`…/version-test`).
- **Export**: the `.bubble` file (Bubble editor → Settings → General → Export application).
- **Test accounts**, one per role, with passwords. Mail access to their inboxes, if offered, lets you read the app's emails.
- **Basic auth**: Bubble can password-protect a whole app version. If the URL answers 401, you need that username and password; it is separate from the user accounts.

Write `.migration/inputs.md`: URL, export file name, each account's email and role, which inbox you can read. Passwords and keys stay out of `.migration/` entirely.

## Safety

Explore only the URL you were given, signed in only as the given test accounts or accounts you sign up yourself. An action with an **external effect** (a payment, an email to an address outside your test inboxes, deleting records you did not create) runs only once you have confirmed the integration is in test mode; a Stripe checkout says so on the page. When you cannot confirm it, record the action as evidence and leave it unclicked.

## Phases

Work through the phases in order. Read each phase file when you reach it, not before; each ends on a completion criterion that must hold before you move on.

1. [`phases/1-inventory.md`](phases/1-inventory.md): static read of the export.
2. [`phases/2-explore.md`](phases/2-explore.md): use the app in a browser as every role.
3. [`phases/3-decide.md`](phases/3-decide.md): personas, assumptions, open questions.
4. [`phases/4-backlog.md`](phases/4-backlog.md): stories, maps, and the final check.

The folder layout and file formats: [`reference/contract.md`](reference/contract.md). Read it before writing anything into `.migration/`.

You are done when `python3 -I <skill-dir>/scripts/check.py .migration` passes and every phase's completion criterion holds. Finish with a short summary: personas, story count by epic, open questions, and anything you could not explore.
