# Phase 4: Backlog

Write the stories, then the maps a builder needs beside them. Formats: [`../reference/contract.md`](../reference/contract.md).

1. **Stories**, one file each in `stories/`:
   - One story per **user goal** ("post a job"). Edit, close or delete get their own story when they have their own rules ("only while open").
   - Every condition you saw on a button or a page is a scenario: who sees it, and when it disappears. Every privacy rule is an "others cannot see" scenario about the data itself: it never reaches their browser, not merely stays off their screen. That is what tells the builder to enforce it on the server.
   - A rule lives in a scenario. When you catch yourself writing a rule in Notes ("only the owner may…", "only while…"), turn it into a scenario instead.
   - Every validation error you hit is a scenario.
   - A page several roles share gets a scenario for each role's view: what each one sees and can change there.
   - Emails, scheduled jobs and webhooks are stories too: persona `system`, written from the point of view of whoever benefits.
   - Built-in features count: sign-up, log-in, password reset.
   - Dead features become `drop-candidate` stories that cite their decision.

2. **`data-model.md`**: each type with its fields, relations and statuses, and who may see it, in plain words.

3. **`workflows.md`**: a mermaid graph from triggers (pages, buttons, schedules, webhooks) to effects (records changed, emails, payments, navigation), plus a line per non-obvious rule.

4. **`integrations.md`**: each external service, email and background job: what triggers it, what it sends, what the new app must replace.

5. **Check** the backlog:

   ```bash
   python3 -I <skill-dir>/scripts/check.py .migration
   ```

   It verifies the story format, that cited evidence and refs exist, that stories use domain words, and that every inventory item is covered by a story or explained in `coverage-notes.md`. It writes `coverage.md`. Fix what it reports and run it again.

Done when `check.py` passes.
