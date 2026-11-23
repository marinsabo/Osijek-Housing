# NNN. Use Brevo for sending emails

## Status

Proposed, 2026-11-22

## Context

OsijekHousing needs to send emails to users for things like new apartment alerts, account verification, and password resets. Our backend runs in FastAPI inside Docker, and we already write our email logic in Python using the standard `smtplib` library in `app/alerts/mailer.py`.

Since this is a student/team project with no budget for infrastructure, we need a service with a permanently free plan that does not ask for a credit card upfront. It also needs a solid daily sending limit for testing and early users, and it should work out of the box over standard SMTP on port 587 without installing extra libraries. At the same time, everyone on the team needs to be able to run and test the project locally without creating their own email provider accounts or sharing API keys.

We looked at four main options:

- **Brevo:** Gives us 300 free emails per day (around 9,000 a month) permanently, needs no credit card, and works directly over standard SMTP.
- **Resend:** Has a great API and gives 3,000 free emails a month, but limits us to 100 emails per day and is built mainly around its own SDK rather than `smtplib`.
- **Mailjet:** Offers 200 free emails per day over SMTP, but puts its own branding at the bottom of every email on the free plan.
- **SendGrid:** Removed its permanently free plan and only offers a 60-day trial now, so it does not fit our budget.

## Decision

We will use **Brevo** as our email provider and connect to its SMTP server (`smtp-relay.brevo.com`, port `587` with STARTTLS) using Python's built-in `smtplib` and `email.message` modules inside `app/alerts/mailer.py`.

All SMTP settings (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, and `SMTP_FROM`) will live in each developer's local `.env` file and get loaded into the Docker container at runtime. Nobody is allowed to hardcode credentials in the code or commit `.env` to GitHub—only `.env.example` with empty secret fields goes into the repo. We also keep `SMTP_USER` (Brevo's technical login) separate from `SMTP_FROM` (the visible sender address) so we can test with a personal Gmail now and switch to an `osijekhousing.hr` domain later just by editing `.env`.

If `SMTP_USER` or `SMTP_PASS` is left empty in `.env`, `send_email` will simply print the recipient, subject, and message body to the terminal instead of trying to connect to Brevo. That way, the rest of the team can test features that trigger emails locally without needing the SMTP password.

We picked Brevo because 300 emails a day gives us the most room for testing on a free plan, and standard SMTP lets us keep our Python code simple.

## Consequences

**Positive:**
- We pay nothing during development and early launch while still getting 300 emails per day.
- We do not have to install or maintain any third-party email libraries in our Docker image.
- Everyone on the team can test email alerts locally with an empty `SMTP_PASS` by just checking the FastAPI Docker logs.
- Moving to a real `osijekhousing.hr` sender address later only requires changing one line in `.env` and adding DNS records in Brevo.

**Negative and Risks:**
- While we send from a personal `@gmail.com` address during development, emails will often land in the recipient's spam folder until we buy and verify our own domain.
- Brevo blocks unknown IP addresses by default and checks new accounts before allowing full sending, so whoever manages the account has to turn off IP blocking in Brevo's security settings.
- Free accounts share IP addresses with other Brevo users, which can occasionally hurt email deliverability compared to paid plans.

**Revisit Criteria:**
- We will revisit this choice if we start sending more than 300 emails a day, if too many emails end up in spam even after adding our own domain, or if we later need delivery tracking webhooks that an API-first provider handles better.