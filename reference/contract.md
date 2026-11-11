# The `.migration/` contract

Stack-neutral output. A build agent for any stack reads only this folder.

```
.migration/
  inputs.md            what you were given (no secrets)
  inventory.json       from scripts/inventory.py (Buildprint workspace or export), unedited
  inventory.md         same, readable
  evidence/
    journal.md         what you did and saw in the app, entry by entry
    *.png              screenshots named after their entry (E012.png)
  personas.md
  decisions.md         assumptions you settled, with evidence
  open-questions.md    what only the owner can answer
  stories/S001-post-a-job.md …
  data-model.md        types, fields, relations, who can see what
  workflows.md         triggers → effects, as a mermaid graph plus notes
  integrations.md      external services, emails, scheduled jobs, webhooks
  coverage-notes.md    inventory refs no story covers, each with the reason
  coverage.md          written by scripts/check.py
```

## Evidence journal

One entry per observation, numbered in order. Cite inventory refs when you know them.

```markdown
## E014
- as: freelancer (sam@…)
- at: /version-test/job/landing-page-1234
- did: sent a proposal, price 450
- saw: form replaced by "You have applied. Status: pending"; proposal listed on my proposals
- refs: wf:job/bTHCK, page:my-proposals
```

## Personas

One `## <Name>` heading per human persona, with: goal, how you found them (role, sign-up choice, page guards), the account you used, and evidence ids. Behaviour no person triggers directly (webhooks, scheduled jobs, emails) belongs to the persona `system`, which needs no heading.

## Decisions and open questions

`decisions.md`: `## D001 <title>`, then the decision, the evidence, and what would change it.

`open-questions.md`: `## Q001 <question>`, then why the rebuild depends on it, what you tried in the app (evidence ids), your recommended answer, and the stories it affects. A question the app can answer is a gap in your exploration: go and find out.

## Story file

`stories/S001-<slug>.md`:

````markdown
---
id: S001
title: Post a job
persona: client
epic: Hiring
priority: must            # must | should | could
status: observed          # observed | inferred | drop-candidate
evidence: [E003, E004]
inventory_refs: [page:post-job, wf:post-job/bTGPZ]
---

As a client, I want to post a job with a title, description, category and budget, so that freelancers can find it.

```gherkin
Scenario: Post a job
  Given I am signed in as a client
  When I post a job with a title, description, category and a budget of 500
  Then it appears as open in my jobs
  And it appears first on the home page

Scenario: Budget must be positive
  When I post a job with a budget of 0
  Then I see an error and no job is created
```

Notes: context a builder needs that is not a rule (rules are scenarios).
````

- **status**: `observed` when you saw it work in the browser (needs `evidence`); `inferred` when only the export shows it, such as a scheduled job or webhook (needs `inventory_refs`); `drop-candidate` for a feature that looks dead (unreachable, unused), backed by a decision.
- **persona** is a persona heading from `personas.md`, lower-cased, or `system`.
- **Words**: the app's own domain words, as a user reads them on screen. The builder chooses the implementation, so the story describes behaviour, never how Bubble builds it.
