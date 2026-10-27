# Phase 1: Inventory

The export tells you everything the app *contains*: pages, what each button does, who may see which data, background jobs, external calls. The browser later tells you what it *means*. The inventory is your map and your coverage checklist.

1. Run the inventory script on the export:

   ```bash
   python3 -I <skill-dir>/scripts/inventory.py <app>.bubble -o .migration/
   ```

   No export? Write an open question asking for one, then build a lighter map in phase 2 from navigation alone, and mark every story's `inventory_refs` empty.

2. Read **all** of `.migration/inventory.md`. As you go, note in a scratch list:
   - the **roles**: role-like option sets, sign-up choices, page-load redirects conditioned on a role;
   - **gated pages**: pages that redirect when you are logged out or in the wrong role;
   - **conditional UI**: elements hidden on load and shown when a condition holds; each condition is a likely acceptance criterion;
   - **privacy rules**: who may see each data type; each is a likely "others cannot see" criterion;
   - **effects**: emails, payments, API calls, scheduled or backend workflows, deletes;
   - **dead-feature hints**: unreachable pages, types nothing creates.

Done when `inventory.md` exists and your scratch list covers every page, every role and every effect it names.
