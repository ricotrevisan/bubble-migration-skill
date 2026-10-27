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

   Before writing a question, ask: could a browser session answer this? If so, go and answer it.

Done when every persona has evidence, every dead-feature hint from the inventory has a decision, and every open question carries a recommended answer.
