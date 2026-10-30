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

   Before you close the file, sweep these sources; each usually yields a question the app cannot settle:
   - **half-built features**: a form or page with no working action. Ask whether the rebuild finishes it, keeps it as it is, or drops it;
   - **names that contradict their use**: a field, page or label whose name says one thing while the app uses it for another. Ask which meaning the rebuild keeps;
   - **fixed numbers that look like policy**: durations, limits, cut-offs and thresholds hard-coded in workflows. Ask whether they stay fixed or become settings;
   - **behaviour that might be a bug**: something you saw that contradicts the app's own labels, messages or other screens. The app shows what happens, not whether it is intended: write what you saw as a decision, and ask whether to keep it.

   Each question passes two gates before it goes in the file:
   - **Rebuild gate**: the rebuild of *today's* app depends on the answer. Ideas for features the app lacks are not migration questions; leave them out, or list them once under "Possible later improvements" at the end of the file. A half-built feature is part of today's app, so its fate passes this gate.
   - **Evidence gate**: you tried to answer it in the app first. Record what you tried (journal entries) under "Tried". If a browser session could settle a *fact* (what happens, who sees what), settle it and write a decision instead. Intent (whether what happens is wanted) stays a question even after you have observed the behaviour.

Done when every persona has evidence, every dead-feature hint from the inventory has a decision, you have swept the four question sources, and every open question passes both gates and carries a recommended answer.
