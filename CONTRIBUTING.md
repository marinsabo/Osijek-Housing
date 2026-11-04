# Contributing

Thanks for working on Osijek Housing. This page is how we work together.

## Before you start

- Follow the [README](README.md) to run the app locally.
- Pick an issue assigned to you on the project board.

## Workflow

1. Pull the latest `main`:
   ```bash
   git switch main
   git pull
   ```
2. Create a branch named after what you're doing, e.g. `add-email-sending`:
   ```bash
   git switch -c add-email-sending
   ```
3. Commit in small steps. A commit title is a plain sentence that says what changed, e.g. "Add a function that sends an email through the provider".
4. Push and open a pull request. Fill in the template, link the issue (`Closes #12`), and say whether and how you used AI tools.
5. Wait for one approval, address the comments, then merge. Nobody pushes directly to `main`.

## Reviews

- Reviews happen within 48 hours. If yours has waited longer, say so in #help.
- When you review, ask questions ("what happens if this list is empty?") rather than rewriting the code for the author.
- `CODEOWNERS` decides who is asked to review. If your change touches code someone else calls, agree it with them first and ask them to review it.

## Where code lives

| Folder         | What                                   | Owner |
| -------------- | -------------------------------------- | ----- |
| `app/core/`    | Data model, listings, accounts, search | Marin |
| `app/web/`     | Pages, templates, CSS                  | Polić |
| `app/alerts/`  | Saved searches, email alerts           | Bob   |
| `app/pricing/` | Fair-rent estimate                     | Sigi  |

Pages display, modules decide: rules about what's valid or allowed live in the owner's module, and pages call them.

Shared files (`docker-compose.yml`, `pyproject.toml`, `.env.example`, `app/main.py`, `.github/`) belong to Marin. Anyone may change them in a PR; Marin reviews it.

## Database changes

Only through migrations. Pull `main` and say so in Discord before you create one. Only one migration PR is open at a time.

## Secrets

Passwords, API keys and other secrets never go in Git, Discord or AI tools. `.env.example` lists setting names only, never values.

## Language

Everything in the repository is in English: code, comments, commits, issues and PRs.

## Stuck?

Say so the same day, in #help or at the weekly sync. While you wait, keep going with fake data.
