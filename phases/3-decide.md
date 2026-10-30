# Phase 3: Decide

Turn what you saw into the frame the backlog hangs on. Settle everything the evidence settles; leave the owner only what it cannot.

1. **Personas** (`personas.md`): the people who use the app, from the roles you found and used. A role nobody can reach (no sign-up path, no account, no page) is a finding for `decisions.md`, not a persona.

2. **Decisions** (`decisions.md`): every judgement the backlog depends on, with its evidence:
   - which features are **dead**: unreachable and unused; they become `drop-candidate` stories, not regular ones;
   - what an ambiguous screen means;
   - which of two overlapping features is the real one;
   - behaviour you inferred from the export but could not trigger.

3. **Open questions** (`open-questions.md`): what only the owner knows, each with your recommended answer. Typical ones:
   - how users sign in after the move (Bubble does not export passwords);
   - which external accounts (payments, email sender) the new app uses, and who switches webhooks at cutover;
   - whether a dead-looking feature can go;
   - intent the app cannot show: the reason behind a rule, a planned change.

   Before you close the file, check for **half-built features**: a form or page with no working action. Ask whether the rebuild finishes it, keeps it as it is, or drops it.

   These are decisions, not questions; write them in `decisions.md` and move on:
   - a legacy name that the app uses for something else: the rebuild keeps the behaviour you observed and may rename it;
   - a fixed number (a duration, a limit, a cut-off): the rebuild keeps today's value as it is;
   - display and navigation preferences (time zones, where a page returns to);
   - behaviour that looks odd but is consistent with the app's own screens: rebuild it as observed;
   - improvements to how today's app works.

   Each question passes two gates before it goes in the file:
   - **Rebuild gate**: the rebuild of *today's* app depends on the answer. Ideas for features the app lacks are not migration questions; leave them out, or list them once under "Possible later improvements" at the end of the file. A half-built feature is part of today's app, so its fate passes this gate.
   - **Evidence gate**: you tried to answer it in the app first. Record what you tried (journal entries) under "Tried". If a browser session could settle it, settle it and write a decision instead.

Done when every persona has evidence, every dead-feature hint from the inventory has a decision, you have checked for half-built features, and every open question passes both gates and carries a recommended answer.
