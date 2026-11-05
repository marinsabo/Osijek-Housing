# 001. Modular monolith

## Status

Accepted, 05-11-2026

## Context

Four people build Osijek Housing. Three of them have never built software before, and one has some experience. Each of us has promised about five hours a week, and the public launch is on 1 June 2027. We expect hundreds of users in the first season, not thousands. The app runs on a single free Oracle Cloud server with 2 OCPUs and 12 GB of memory.

The work splits naturally into four areas, each with one owner: core (data model, listings, accounts, search) for Marin, web (pages, templates, CSS) for Polić, alerts (saved searches, email) for Bob, and the fair-rent estimate for Sigi. The areas depend on each other. Pages show listings and estimates, and alerts reuse the search to decide which listings match a saved search.

Two forces pull against each other. Beginners with little time need to focus on one area and a small set of tools, and they need to know what is theirs. But the parts have to work together as one product, and only one person (Marin) has time to run infrastructure.

We considered three ways to organise the code.

A plain monolith is one application with no agreed boundaries inside it. It is the simplest to start, but with four people working in it, code that belongs to one area ends up depending on another area's internals. A change in one place then breaks something elsewhere, and nobody is clearly responsible for it.

Microservices would make each area a separate application with its own deployment, usually its own database, and calls over the network between them. Each beginner would have to learn networking between services, separate deployments and failure handling before they could change anything. Marin would have to deploy and monitor four services on one small server. These costs buy independent scaling and independent deployment, and we need neither at a few hundred users.

A modular monolith is one application, deployed once, whose code is divided into modules with clear owners and agreed ways of calling each other.

## Decision

We will build Osijek Housing as a modular monolith: one FastAPI application in one repository, using one PostgreSQL database and deployed as one unit.

The application is divided into four modules, `app/core/`, `app/web/`, `app/alerts/` and `app/pricing/`. Each module has one owner, recorded in `CODEOWNERS`, who must review every change to it.

Modules call each other only through the functions the owning module offers for that purpose, such as the core functions for creating and searching listings. A module does not import another module's internal helpers and does not query another module's tables directly. Rules about what is valid or allowed live in the module that owns the data. Pages display those results and do not repeat the rules.

The database schema has one owner, Marin. Other people may write migrations for their own tables, such as Bob's saved-search tables, but every migration needs Marin's review before it is merged.

Bob's alert worker is part of the monolith. It is the same codebase started as a separate process, and it reaches listings through the same core functions as the pages.

## Consequences

Each person can work and learn inside one folder, with one set of tools, and knows exactly what they own. When something in an area goes wrong, it is clear who to ask, and `CODEOWNERS` brings the right reviewer into every pull request automatically.

There is one thing to run locally (`docker compose up`), one thing to deploy and one place to read logs. Debugging a request that crosses modules means following ordinary Python function calls, not requests between services. Tests can call any module's functions directly against one test database.

The boundaries are only as strong as our discipline. Nothing in Python stops Polić from importing an alerts helper or querying a table directly, so code review is the only thing that enforces the rules above. If reviews let shortcuts through, the code slowly turns into the plain monolith we rejected.

Because the modules call each other's functions, those functions are contracts. Changing a core function's name, inputs or errors can break another person's code, so the owner must agree such changes with the people who call it before merging.

Everything shares one process and one deployment. A crash at startup in any module takes the whole site down, and a slow query in one area slows every page. All modules also share the one server's resources. At a few hundred users we accept this, and CI tests on every pull request are our first defence.

Marin is a likely bottleneck, because the schema, the core functions and the infrastructure all need Marin's review. Teammates' review requests therefore come before Marin's own coding.

We will revisit this decision if one module needs to scale or be deployed on a different schedule from the rest. Another trigger is the alert worker's load hurting page response times in a way that a separate process on the same server cannot fix. If that happens, the agreed function boundaries are where a module would be cut out.
