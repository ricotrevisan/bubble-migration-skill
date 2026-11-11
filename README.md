# bubble-migration

An agent skill that turns an existing Bubble.io app into a stack-neutral
migration backlog: personas, user stories with acceptance criteria and
evidence, the data model, a workflow map, integrations and open questions.

The agent reads the app's source, then uses the running app in a browser as
each role, and writes everything to `.migration/`. A team, or a build agent,
can rebuild the app on any stack from that folder.

It uses the [Buildprint](https://buildprint.ai) CLI by default: it clones the
app into a BubbleScript workspace (no export needed), signs in as test users,
reads the app's emails and its server logs. Without Buildprint it falls back
to the `.bubble` export and plain Python.

## Install

Copy this folder into your agent's skills directory, for example
`.claude/skills/bubble-migration/` in your project.

## Use

Give your agent:

- the app URL (the `version-test` one),
- the app's source: its Buildprint app ID and branch, or the `.bubble` export
  (Bubble editor → Settings → General → Export application),
- one test account per role,
- the app's basic-auth username and password, if it has one,

and ask it to build a migration backlog. It needs Python 3 and a browser tool;
`buildprint` is optional but preferred.

## Scripts

- `scripts/inventory.py <workspace-or-app.bubble> -o .migration/`: static
  inventory from a Buildprint workspace (`buildprint project clone` or
  `buildprint open`) or straight from the export. Same refs either way.
- `scripts/check.py .migration`: checks the backlog and writes `coverage.md`.

Both use only the Python standard library.
