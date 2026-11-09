# 002. Why this stack

## Status

Accepted.

## Context

ADR 001 decided that Osijek Housing is one application with one database. This ADR decides which tools that application is built with.

None of us has built anything with these tools before, so we are choosing them from their documentation, their popularity and our constraints, not from experience. Three of the four team members are beginners, and each of us has about five hours a week. The app has to run on one small server with 2 OCPUs and 12 GB of memory, and it has to answer distance questions such as "which flats are within 2 km of FERIT".

Two forces pull against each other. We want to learn tools that real projects use today, because that is part of why we are doing this. But a beginner with five hours a week cannot spend the first month learning the tools before writing any useful code. We are looking for the middle ground: tools that are widely used, but that a beginner can get started with by following the official tutorial.

For the language, Python was the realistic choice because it is the one the whole team can already read or learn fastest. For the web framework we looked at three Python options. Django includes almost everything (an admin, accounts, forms, an ORM), but it is large, and much of it has to be learned before you can change anything. Flask is small and simple, but most features come from separate extensions that we would have to choose and combine ourselves. FastAPI is also small, has one tutorial that covers what we need, and checks the data each request receives using ordinary Python type hints.

## Decision

We will use Python 3.12 for all code. Everyone runs the app through Docker, which starts the same Python version from the `Dockerfile`, so differences between our laptops do not matter.

We will use FastAPI as the web framework. It is lighter than Django, and unlike Flask it validates input and documents the endpoints out of the box. Pages will be rendered on the server from HTML templates inside `app/web/`, so the whole team works in one language and there is no separate JavaScript application to build and deploy.

We will use PostgreSQL with the PostGIS extension as the database, because PostGIS can store a flat's location and measure distances in a query. We will use SQLAlchemy to work with the database from Python and Alembic for migrations, which are the standard pair for this in Python. Tests will use pytest and run against a real test database.

We will use Docker Compose to run the app and the database, locally and on the server. Everyone gets the same database and the same setup with one command, and what we test locally is what runs in production.

The other choices (SQLAlchemy, Alembic, pytest) follow the advice of more experienced programmers and are the most common choices for a Python web app. We have not compared them with alternatives ourselves.

## Consequences

Everyone works in Python, and each tool has an official tutorial that the roadmaps point to. New teammates only need Docker installed to run the whole project.

FastAPI does not come with accounts, an admin panel or protection for forms, which Django would have given us. We have to build or add these ourselves, which takes time and is security-sensitive. The roadmap plans for this (accounts in Phase 1, form protection in Phase 2), and we will follow the OWASP cheat sheets when building them.

We expect the web part to be the hardest for a beginner, because server-rendered pages require HTML and CSS on top of Python and templates. Polić owns most of the pages, so his work should be split into small issues and get help first if he gets stuck.

Docker must run on every teammate's laptop. If someone's machine cannot run it, that person is blocked until it is fixed.

This ADR does not decide how we list and pin Python dependencies. For now the `Dockerfile` installs packages without fixed versions, so two builds can end up with different versions. That needs its own decision soon.

We will revisit this decision if a tool turns out to cost us much more time than it saves. One example is if building accounts and form protection ourselves becomes so slow that Django's built-in versions would have been cheaper. Another is if server-rendered pages cannot do something the MVP needs, such as the map pin.
