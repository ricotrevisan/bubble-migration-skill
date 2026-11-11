# bubble-migration

An agent skill for moving an app off Bubble. Your coding agent reads the app's
editor data, uses the app in a browser as each of its user roles, and writes a
**migration backlog**: everything a developer needs to rebuild the app on
another stack, without opening the Bubble editor.

Works with any agent that supports [Agent Skills](https://agentskills.io)
(Claude Code, Codex, Cursor and others).

## What you get

A `.migration/` folder of plain Markdown, describing the app as it behaves on
the version you point it at:

| File | What's in it |
|---|---|
| `personas.md` | Who uses the app (one per role) and what they want |
| `stories/S001-….md` | One user story per goal, with acceptance criteria as Gherkin scenarios, priority and evidence |
| `data-model.md` | Every data type and option set, their fields, the status values a record moves through, and who may see what (your privacy rules, in words) |
| `workflows.md` | A Mermaid map from triggers (buttons, schedules, webhooks) to effects (records, emails, payments) |
| `integrations.md` | API Connector calls, plugins, emails, webhooks and scheduled jobs, and what must replace each |
| `open-questions.md` | What only you, the owner, can answer, each with a recommended answer |
| `decisions.md` | What the agent settled itself, and the evidence for it |
| `evidence/journal.md` | Every action the agent took in the app and what it saw |
| `coverage.md` | Every page, workflow, data type and API call, and the story that covers it |
| `coverage-notes.md` | Why the rest isn't covered: unreachable, needs a live payment, looks dead |

The stories describe behaviour in the app's own words, never Bubble mechanics
("Withdraw request", not "Make changes to Current page's Request"), so you can
build on Rails, Phoenix, Next.js or anything else. A story looks like this:

````markdown
---
id: S012
title: Withdraw my request
persona: staff
priority: must
status: observed            # seen working in the browser
evidence: [E023, E024, E034]
---

As a staff member, I want to withdraw a request that is still waiting for
approval, so that its reserved budget is freed when I no longer need it.

```gherkin
Scenario: Only while awaiting approval
  Given my request is a draft, approved, received, rejected or canceled
  Then "Withdraw request" is not offered and the request cannot be withdrawn

Scenario: Withdrawing twice changes nothing
  Given I withdrew my request in another tab
  Then this tab shows "Canceled" without a withdraw button
  And no second release of budget happens
```
````

On our test apps (about 12 pages, 4 roles) a run took 20 to 45 minutes and
cost US$4 to 6 with Claude Opus, and produced 25 to 35 stories. We haven't
measured large apps yet; expect cost to grow with pages and roles. There is no
resume: if a run dies, start again in a fresh folder.

## Before you start

1. **Use the development version.** The agent works on `version-test` and
   its database: it signs up users and creates, edits and cancels records,
   which runs your workflows and uses workload units. Seed it with enough
   data that every list and dashboard shows something.
2. **Check what your workflows call.** Backend workflows that hit Zapier,
   Make, webhooks or an API with the same key in development and live will
   fire for real. Where API Connector lets you, set a separate development
   key, and point webhooks at test endpoints.
3. **Make one test account per role.** A role here is any kind of user who
   sees different pages or data: a `role` option set on User, an `is admin`
   yes/no, company membership. Without Buildprint, use email-and-password
   accounts that are already confirmed; the agent can't sign in with Google
   or other social logins.
4. **Know what the agent sees.** It reads your whole app definition,
   including API Connector keys, and the data on every page it opens. All of
   that goes to your AI model provider. It never writes keys or passwords
   into `.migration/`. If the development database is a copy of live data,
   or it's a client's app, get the owner's consent first.
5. **Have Python 3** and a browser your agent can drive. If you have none,
   [agent-browser](https://github.com/vercel-labs/agent-browser) works well:
   `npm install -g agent-browser && agent-browser install`.

## Give it your app

Pick one.

- **With [Buildprint](https://buildprint.ai)** (recommended). The agent pulls
  the app straight from Bubble, signs in as your test users with Bubble's
  "Run as" (no passwords needed, and social-login users work), gets its own
  inbox for the app's emails, and reads your Bubble server logs to see
  backend workflows run. You need a Buildprint account with your app
  connected (see their docs). Then, once:

  ```bash
  npm install -g buildprint
  buildprint link              # sign in to your Buildprint account in the browser
  buildprint project list      # your app should be listed
  ```

  You then pass the app ID, the `id=` in the editor's URL
  (`bubble.io/page?id=myapp…`), and the branch: `test` for the main
  development version, or the `version=` value in the editor's URL for
  another branch.

- **With an export.** In the Bubble editor: Settings → General → Export
  application. Pass the `.bubble` file. If `buildprint` is installed, the agent
  reads the export through it, no account needed; if not, it uses plain Python.

## Install

Clone the skill into your agent's skills folder:

```bash
# Claude Code, for all your projects
git clone https://github.com/ricotrevisan/bubble-migration-skill ~/.claude/skills/bubble-migration

# Codex and other agents that read ~/.agents/skills
git clone https://github.com/ricotrevisan/bubble-migration-skill ~/.agents/skills/bubble-migration
```

`git pull` in that folder updates it.

## Run

Make an empty folder and start your agent in it; it writes `.migration/`
(the backlog) and, with Buildprint, `.migration-src/` (a read-only copy of the
app) there. Then paste this prompt and fill in the brackets:

```text
Use the bubble-migration skill to build a migration backlog for my Bubble app.

- App URL: https://[myapp].bubbleapps.io/version-test
- Source: Buildprint app [myapp], branch test
  (or: the export at [path/to/myapp.bubble])
- Test accounts (passwords not needed with Buildprint):
  - [role]: [email] / [password]
  - [role]: [email] / [password]
- Inbox: [none, or how to read the test accounts' email]
- Site password on version-test: [none, or username / password]
- Browser: [agent-browser, or the browser tool you use]

Work autonomously. Put anything only I can answer in open-questions.md.
```

"Site password" is the username and password you can set in Settings →
General to lock a whole app version; it's separate from user accounts.

The agent asks once for anything missing, then keeps going. When it finishes,
it prints a summary: personas, stories per epic, open questions, and anything
it couldn't explore.

## Safety

- It opens only your app's URL (and the pages your app sends it to, such as
  a checkout), signed in as your test accounts or users it signs up itself.
- Anything with an effect outside the app (a payment, an email to an address
  outside its test inboxes) and deleting records it didn't create: it does
  these only after it has seen the integration is in test mode (a Stripe
  checkout says so on the page). Otherwise it notes the action and leaves it
  unclicked. It can't tell whether a backend workflow's call reaches a live
  service, so do step 2 of "Before you start".
- With Buildprint it only reads: it never applies changes to your app,
  restores savepoints or changes secrets.

## After the run

1. Answer `open-questions.md`, and correct anything in `decisions.md` you
   disagree with.
2. Skim `coverage.md` and `coverage-notes.md` for parts of the app the agent
   couldn't reach.
3. Hand `.migration/` to whoever builds the new app, person or agent. The
   stories are the spec; `data-model.md` and `integrations.md` are the
   checklist for data migration and third-party accounts.

## For contributors

The agent runs these itself; you don't need to.

- `SKILL.md` and `phases/` are the instructions; `reference/contract.md`
  defines the `.migration/` format.
- `scripts/inventory.py <workspace-or-app.bubble> -o .migration/` lists every
  page, workflow, data type and API call, from a Buildprint workspace or the
  export.
- `scripts/check.py .migration` checks the backlog and writes `coverage.md`.
- `tests/` run in CI: `python3 -I tests/lint_skill.py` and
  `python3 -I tests/test_inventory.py`.

Scripts use only the Python standard library. MIT licensed.
