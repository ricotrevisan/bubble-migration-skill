# bubble-migration

An agent skill that turns an existing Bubble.io app into a stack-neutral
migration backlog: personas, user stories with acceptance criteria and
evidence, the data model, a workflow map, integrations and open questions.

The agent reads the app's `.bubble` export, then uses the running app in a
browser as each role, and writes everything to `.migration/`. A team, or a
build agent, can rebuild the app on any stack from that folder.

## Install

Copy this folder into your agent's skills directory, for example
`.claude/skills/bubble-migration/` in your project.

## Use

Give your agent:

- the app URL (the `version-test` one),
- the `.bubble` export (Bubble editor → Settings → General → Export application),
- one test account per role,
- the app's basic-auth username and password, if it has one,

and ask it to build a migration backlog. It needs a browser tool and Python 3.

## Scripts

- `scripts/inventory.py app.bubble -o .migration/`: static inventory of the export.
- `scripts/check.py .migration`: checks the backlog and writes `coverage.md`.

Both use only the Python standard library.
