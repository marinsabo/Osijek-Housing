# 003. Data model v1

## Status

Proposed

## Context

Every module in Osijek Housing uses the same PostgreSQL database (ADR 001), so the data model is the contract the whole team builds on. Changing a table after someone has written code against it means a migration and rewritten code in several modules. The model therefore has to be agreed early, before the core functions that everyone calls.

Each teammate depends on it in a different way. Polić's pages decide what a landlord fills in and what a student sees, so every field on a page needs a column. Bob's saved searches store the same filters as the search, and his worker has to tell which listings are new. Sigi's fair-rent estimate reads the details of flats and listings, such as area, rooms, neighbourhood and price.

The model was meant to be built from four inputs: Polić's page sketches, Sigi's neighbourhood list, the listing details Sigi's estimate needs, and Bob's alert needs. None of them had arrived when this model was written. The fields instead come from Marin's earlier web development experience, Marin's own research on Osijek neighbourhoods, and a first guess at what alerts need. Waiting would have delayed the core functions the others are waiting for, so the model was written first and will be checked against those inputs when they arrive.

Several questions had more than one reasonable answer: whether a flat and a listing are one table or two, whether reviews belong to a flat or a listing, how to store a location, and how to check that a reviewer really lived in a flat. The options are described with each decision below.

Some data was left out on purpose to keep the MVP small, for example students' nationality and living preferences. That data would be useful for roommate matching, which is planned after the MVP, and can be added then with a migration.

## Decision

We will use the model in [`docs/data-model.dbml`](../data-model.dbml). Its main decisions are the following.

**Users and roles.** Every person has one row in `users`. Students and landlords also have a row in `student` or `landlord`, holding the data only that role needs: a student's faculty, a landlord's phone number and verification. Moderators are users with `is_moderator` set. A single `users` table with a role column was the alternative, but it would need columns that are empty for every other role.

**Flats and listings.** A flat is the physical place, and a listing is one offer to rent it at a price. Prices and descriptions change from year to year, but the flat stays the same, so when a flat is rented again the landlord creates a new listing for the same flat. One table for both would copy the flat's details into every new offer and lose the link between them. A listing is open while both `taken_at` and `archived_at` are empty: `taken_at` means the flat was rented through it, and `archived_at` means the landlord withdrew it. Keeping the two apart means a withdrawn offer is never counted as a real rental price.

**Reviews belong to flats.** A listing is taken, replaced or deleted after a season, and reviews attached to it would disappear with it. A landlord could then get rid of a bad review simply by publishing a new listing. Reviews stay with the flat and describe it as it was when they were written. A student may review a flat only once.

**Location.** A flat's location comes from the landlord's map pin and is stored as `geography(Point, 4326)` with a GiST index, so PostGIS can answer "which flats are within 2 km of FERIT" directly in metres. Faculty locations are stored once, in `faculty`. Storing latitude and longitude as two plain numbers was the alternative, but every distance query would then need its own formula and could not use a spatial index.

**Search filters and their units.** Pages, Bob's saved searches and the search all use the same filters, in the same units:

- price: euros per month, rent only, unless the listing has `utilities_included` set
- rooms: a whole number
- distance: kilometres from one chosen faculty
- neighbourhood: zero or more neighbourhoods from the `neighbourhood` table, by id. None selected means any neighbourhood.

Utilities are not part of the price, because they differ from flat to flat and depend on how many people share it. Students agree them with the landlord directly. A landlord whose price already includes utilities ticks `utilities_included` on the listing. The flag is only displayed, not used as a filter, so a price with utilities included is compared like any other. It is stored from the first listing so that Sigi's estimate can leave those prices out or adjust them.

A listing matches when it passes every filter that is set. Saved searches store their neighbourhoods in a join table, `saved_search_neighbourhood`, so every id is checked by a foreign key.

A flat's neighbourhood is chosen by the landlord from the `neighbourhood` list, not worked out from the map pin. The final list comes from Sigi. Until it arrives, the list from Marin's own research is used.

**Review verification.** When a student submits a review, they get an automated email asking for proof that they lived in the flat: a rental contract, a residence registration or a utility bill. The student replies with the proof, a moderator checks it and records `verified_at` and `verified_by`, and the email is then deleted because it contains personal data. Unverified reviews are shown with an "unverified" label and ranked below verified ones. The proof comes from the student, not the landlord, so a landlord can't block bad reviews and never learns who wrote one.

**Moderation.** Moderators hide reviews that use insulting language, reveal personal data or are shown to be false. Hiding sets `hidden_at` and `hidden_by` and can be undone. Users report a review through the `report` table, and resolving a report is separate from hiding the review.

**Deleting accounts and flats.** When a student deletes their account, their reviews stay and are shown as written by "Deleted User", because they are still useful to the next tenants. A landlord cannot delete a flat that has reviews, because deleting it would be a way to get rid of bad ratings. Instead, a landlord can archive a flat, which sets `archived_at`. An archived flat no longer appears in the feed or in search, but the flat and its reviews are still shown on the landlord's profile. The reference from `review` to `flat` restricts deletion, so the database refuses to delete a reviewed flat even if the check in Python is skipped. A flat without reviews can still be deleted. Archived flats can be un-archived. Students can still write reviews if the flat is archived, so archiving can't be used to stop new reviews.

An archived flat never has an open listing. Archiving a flat also archives its open listing, and un-archiving does not reopen it: the landlord creates a new listing instead, so last year's offer never comes back into search. Creating a listing on an archived flat is rejected. The database can't check a rule that spans two tables, so this rule lives in the core functions, and no other code may write listings directly.

**Login codes.** Codes are stored hashed in `login_code`, with the email they were sent to and no link to `users`, because a code is also sent at sign-up, before the user exists. Rows are deleted after use or expiry. How sessions work is decided in ADR 004.

**Photos.** Each listing photo is one row in `listing_photo`, ordered by `position`. The image file itself is stored outside the database. Where it is stored and how large it may be is decided before 6 December.

**Rules in the database.** Checks, such as a price above zero and a rating from 1 to 5, and unique indexes, such as one review per student per flat, are part of the model. They stop invalid data even when a bug or a script skips the checks in Python.

## Consequences

Renting a flat again adds a row instead of copying one, and a flat's reviews carry over from one listing to the next.

Distance search can be written once as a single query, which is the one definition of "matches the filters" that both the pages and Bob's worker use.

Every lookup that needs a student's faculty or a landlord's phone number joins two tables. At a few hundred users this cost is not noticeable.

Review verification is manual. Every review adds work for a moderator, and a mailbox holds sensitive documents until they are checked. If reviews arrive faster than moderators can check them, unverified reviews pile up and we will need a faster process.

A review whose author deleted their account can no longer be traced to anyone, so a moderator who hides it cannot contact the author.

The model was written without the teammates' inputs, so it will probably change once they arrive. Until this ADR is accepted, Polić, Bob and Sigi should treat the names as a draft. After that, every change goes through a migration that Marin reviews, and a change to a table someone else's code reads is agreed with them first.

The DBML file describes v1. Once Alembic migrations exist, the models in `app/core/` and the migrations are the source of truth, and the DBML file is not kept up to date.

We will revisit this model when booking is added, since a record of who rented which flat could replace emailed proof, when listings can be reported, or when roommate matching needs student preferences. If landlords' chosen neighbourhoods often don't match their map pins, we will store neighbourhood boundaries and work out the neighbourhood from the pin instead.
