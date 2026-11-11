# Phase 1: Inventory

The app's source tells you everything the app *contains*: pages, what each button does, who may see which data, background jobs, external calls. The browser later tells you what it *means*. The inventory is your map and your coverage checklist.

1. Get a Buildprint workspace, then run the inventory script on it. Take the first route that works:

   - **Linked project** (default): `buildprint project clone <appId> --branch <branch> --dir .migration-src`.
   - **Export, Buildprint installed**: `buildprint open <app>.bubble --dir .migration-src`.

   Either puts one workspace (the folder holding `.buildprint/`) inside `.migration-src/`; it is a read-only copy, not part of the backlog. Then:

   ```bash
   python3 -I <skill-dir>/scripts/inventory.py .migration-src -o .migration/
   ```

   **Fallback**, no `buildprint` or both routes fail: run the script on the export itself.

   ```bash
   python3 -I <skill-dir>/scripts/inventory.py <app>.bubble -o .migration/
   ```

   Both inputs give the same refs. Note in `inputs.md` which route you used. No source at all? Write an open question asking for one, then build a lighter map in phase 2 from navigation alone, and mark every story's `inventory_refs` empty.

2. Read **all** of `.migration/inventory.md`. As you go, note in a scratch list:
   - the **roles**: role-like option sets, sign-up choices, page-load redirects conditioned on a role;
   - **gated pages**: pages that redirect when you are logged out or in the wrong role;
   - **conditional UI**: elements hidden on load and shown when a condition holds; each condition is a likely acceptance criterion;
   - **privacy rules**: who may see each data type; each is a likely "others cannot see" criterion;
   - **effects**: emails, payments, API calls, scheduled or backend workflows, deletes;
   - **dead-feature hints**: unreachable pages, types nothing creates.

3. **With a workspace**, use it beside the inventory:
   - The BubbleScript files (`pages/`, `reusable-elements/`, `backend-workflows/`, `data-types/`, `api-connector/`) show the full expressions and conditions when an `inventory.md` line is too terse. Search them with `grep`.
   - Run `buildprint audit` in the workspace folder. Its privacy and public-endpoint findings are leads for "others cannot see" scenarios and for phase 2 checks, not bugs to fix.

Done when `inventory.md` exists and your scratch list covers every page, every role and every effect it names.
