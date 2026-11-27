# 005. Log in with AAI@EduHr for students and a one-time email code for landlords

## Status

Proposed, 2026-11-27

## Context

Osijek Housing has two kinds of users who need accounts. Students write reviews and save searches, and a review only means something if it comes from a real student. Landlords publish flats and listings, and a fake landlord account could publish fake offers. The login therefore has to do two jobs: let people back in, and check that a student really is a student.

The data model (ADR 003) already expects a login without passwords: `users` has no password column, and `login_code` stores hashed one-time codes with an expiry and an attempt counter. Polić's first login page asks for an email and sends a code. Bob's `send_email()` (ADR 004) can deliver the codes. What is still open is how students and landlords prove who they are, how a logged-in user is remembered between requests, and which pages Polić has to build.

The team is four students with about five hours a week each, and none of us has built authentication before. Anything we build ourselves has to be simple enough to review and test, because a mistake here exposes every account.

The realistic options for proving who someone is were:

- **Passwords:** familiar to users, but we would have to store them safely, build password reset, and protect against reused and guessed passwords. Password reset needs email anyway.
- **A one-time code sent by email:** nothing secret is stored for long, and receiving the code proves the person owns the address. For students, a faculty address would also suggest they belong to a faculty, but only while the address works, and we would have to keep our own list of every faculty's email domains.
- **AAI@EduHr:** the login system of Croatian higher education, run by Srce. The student logs in on the AAI@EduHr page with their university account, and the federation tells us who they are and that they are a student, so the proof comes from the university itself. Organisations outside the federation can register a service if they declare they will follow its rules, and the service has to be registered and checked before it is used in production. It only covers people with a university account, so landlords can't use it.

For remembering a logged-in user, the options were a signed cookie that holds the user's id, which needs no table, or a random token in the cookie that points to a row in a `session` table. A signed cookie can't be cancelled before it expires: logging out only deletes it from one browser.

## Decision

Students will log in with AAI@EduHr. Landlords will log in with a one-time code sent to their email. There are no passwords.

**Students.** The login page has a "Log in with AAI@EduHr" button that takes the student to the AAI@EduHr login page. When AAI@EduHr confirms them, we look the student up by the unique id the federation gives us. The first time, we create their account from the details AAI@EduHr sends, so there is no separate sign-up form. We accept only people the federation marks as students, and their faculty is taken from the institution it reports. We will register the service with AAI@EduHr through Srce and follow its rules.

**Landlords: two flows.** Sign-up asks for an email and the landlord's details, sends a code, and creates the account only after the code is confirmed, so a mistyped or fake address never becomes an account. Login asks only for an email and sends a code. Both flows share the page where the code is entered. A landlord may use any email address, except one from a domain on a public list of disposable email services. Landlords are still verified by a moderator, as described in ADR 003, because a real address doesn't prove someone owns a flat.

**The code.** A code is 6 digits and is valid for 5 minutes. After 3 wrong attempts it stops working, and the landlord has to ask for a new one. Each email has at most one active code: asking for a new code cancels the old one. An email can be sent at most 3 codes in 15 minutes. Codes are stored only as hashes and deleted after use or expiry. Together, these limits allow at most 9 guesses per email in 15 minutes against a million possible codes, and stop the site from being used to flood someone's inbox.

**Not revealing who has an account.** If someone tries to log in as a landlord with an email that has no account, the page shows "If an account exists for this email, we've sent a code" and nothing is sent. If someone signs up with an email that already has an account, the page shows the usual message, and the address receives a short email saying an account already exists and how to log in. In both cases, the page looks the same whether or not the account exists, so the site can't be used to find out who uses it.

**Staying logged in.** Both kinds of users get the same kind of session. After a successful login, we create a row in a new `session` table with a long random token, the user, and an expiry 30 days later. The cookie holds only the token, and is set with `HttpOnly`, `Secure` and `SameSite=Lax`. Logging out deletes the row. A moderator can end all of a user's sessions by deleting their rows. We chose a table over a signed cookie because logging out and banning someone must take effect immediately.

**Where the logic lives.** Handling the AAI@EduHr response, signing up landlords, sending and checking codes, logging in, logging out and finding the current user are functions in `app/core/`. Polić's pages call them and show the result, following the rule that pages display and modules decide. Errors such as a wrong or expired code, an email that isn't allowed, or an AAI@EduHr user who isn't a student are raised as `InvalidInput`, so pages show them the same way as listing errors.

**Pages.** Polić builds five: log in (the AAI@EduHr button for students, and an email field for landlords), landlord sign-up (email, first and last name, phone number), enter code (shared by both landlord flows, with a link to send a new code), an error page for a failed AAI@EduHr login, and a log-out button in the shared layout.

## Consequences

Nobody has to remember a password, and we never store one, so there is no password reset to build and no password list that could leak. A student's account is confirmed by their university, which makes reviews more trustworthy than an email check would.

We have to build two login methods instead of one. AAI@EduHr uses SAML, a standard none of us has worked with, and we will need a Python library for it. That is the hardest part of accounts, and it should be built and tested early.

AAI@EduHr needs our service to be reachable at a public HTTPS address before students can log in, because it sends them back to that address after login. Student login can't work until the domain, the server and HTTPS exist, so those can no longer wait until the end of the MVP. Registration also depends on Srce, which takes time we don't control, so we contact them first, at aai@srce.hr. Until it works, students can be tested with fake accounts on the local machine.

What AAI@EduHr sends about a user, and in what form, still has to be confirmed: the unique id, name, email, whether the person is a student, and their institution. The `faculty` table may need a column for the institution's AAI@EduHr identifier, and `faculty.email_domain` may no longer be needed. Students who graduate lose their AAI@EduHr account, and with it access to ours, but their reviews stay.

Landlord login depends on email. If Brevo is slow or a code lands in spam, the landlord can't log in. While emails are sent from a personal address without our own domain, spam folders are likely, so the pages should tell landlords to check theirs.

We need a migration for the `session` table, and somewhere to keep a landlord's sign-up details until the code is confirmed, either new columns on `login_code` or a small table for pending sign-ups. That choice is made when the account functions are built. Expired sessions, codes and pending sign-ups have to be deleted regularly, or the tables keep growing.

The disposable email list has to be updated now and then, because new services appear. It doesn't stop someone from using a normal free address for a fake landlord account. Moderator verification is what covers that.

The sending limit is per email address, not per visitor. Someone could still make the site send codes to many different addresses. If that happens, we will add a limit per IP address.

The `Secure` cookie flag means the browser only sends the cookie over HTTPS. Locally, the site runs on plain HTTP, so the flag has to be turned off in development through a setting, and that setting must never be off on the server.

We will revisit this decision if registering with AAI@EduHr takes too long for the pilot, in which case students would log in with a code sent to their faculty email until it works, or if email delivery for landlords becomes unreliable.
