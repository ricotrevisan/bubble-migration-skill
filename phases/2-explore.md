# Phase 2: Explore

Use the app the way its people do, one role at a time, and write down what you see. This is where stories come from; the inventory only checks you missed nothing.

## Driving a Bubble app in a browser

- **Basic auth**: open the bare app root with the credentials in the URL first (`https://user:pass@app.bubbleapps.io/version-test`). The browser then reuses them for the origin. A deeper path such as `/index` redirects, and the redirect drops the credentials.
- **Inputs commit on blur**: after filling a field, press Tab before clicking a button, or the app sees an empty input.
- **Settle time**: Bubble updates the page a second or two after a click. Wait, then read.
- **Lists** render one block per item; reading the page's text is usually enough to tell what a list shows.
- **Emails**: links in Bubble's emails go through a click-tracking redirect; open them as they are.
- **Privacy**: data hidden by a privacy rule never reaches the browser. To check that one user cannot see another's records, search the page's HTML for a value you know belongs to someone else.

## Pass A: as a user

For the logged-out visitor, then each account:

1. Sign in (sign up first if the user is new: sign-up is a story too).
2. Visit everything the navigation offers this role. On each page, read what is shown and why it is shown to *this* role. A page several roles share (a profile, a detail page) usually shows each role something different: journal what this role sees there.
3. Do each thing the page lets you do, with realistic values: create, edit, change status, cancel. Prefer records you created; name them so you recognise them (`QA Logo for a café`).
4. Probe each form once with a required field empty, once with an invalid value, and once with a value that must be unique but is taken (an email that already has an account, a duplicate entry); note each error.
5. Open the other roles' pages by URL and note what happens.
6. **Repeat and stale actions**: for each action that changes a status, do it twice, and do it again from a page you loaded before the status changed (keep an old tab, or use Back). Note whether the second attempt is refused and what it says.
7. **Selection rules**: when the app picks one record out of several on its own (next in a queue, an assignment, who gets an offer), find out the order it uses and which candidates it skips and why. Set up a candidate who should be skipped ahead of one who should not, and see who is picked and whether the skipped one keeps their place.
8. When an action should send an email and you can read the inbox, check it arrived and what it says.

Write an entry in `evidence/journal.md` for every observation, as you go, with the inventory refs you recognise. Screenshots help for anything visual.

## Pass B: coverage

Compare the journal with the inventory. For each page and each workflow that changes data, navigates or has an effect, and that no entry cites yet:

- reach it now and journal it; or
- record in `coverage-notes.md` why you cannot: needs a live payment, runs in the background, nothing links to it, needs a role you lack.

Background and scheduled workflows cannot be clicked: read what they do in the inventory and look for their effects (a status that changes, an email that arrives). Wait a few minutes at most; anything due later is `inferred` from the export.

Done when every page, every role and every data-changing workflow in the inventory is cited by a journal entry or explained in `coverage-notes.md`.
