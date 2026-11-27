# Osijek Housing

A website for students looking for a flat in Osijek: listings with a map, search by price, rooms and distance to a faculty, a fair-rent estimate, email alerts for new listings and reviews of flats.

## Running it locally

### Prerequisites

You need:

- **Git**
- **Docker**: Docker Desktop on Windows and macOS, Docker Engine with the Compose plugin on Linux

|         | Git                                                | Docker                                                                                   |
| ------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Windows | [Install Git](https://git-scm.com/install/windows) | [Install Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) |
| macOS   | [Install Git](https://git-scm.com/install/mac)     | [Install Docker Desktop](https://docs.docker.com/desktop/setup/install/mac-install/)     |
| Linux   | [Install Git](https://git-scm.com/install/linux)   | [Install Docker Engine](https://docs.docker.com/engine/install/)                         |

On Linux, follow the [post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/) so you can run `docker` without `sudo`.

### 1. Clone the repository

```bash
git clone https://github.com/marinsabo/Osijek-Housing.git
cd Osijek-Housing
```

### 2. Create your `.env` file

The app reads the database credentials from a `.env` file. Credentials never go in Git, so the repository only has `.env.example`, which lists the setting names without values.

Copy it:

```bash
cp .env.example .env
```

On Windows, use PowerShell or Git Bash for this command, or copy the file in your file explorer.

Open `.env` in your editor and fill in the values. Any values work locally, for example:

```
POSTGRES_ADMIN_USER=postgres
POSTGRES_ADMIN_PASS=change-me
```

Don't use spaces or quotes. `.env` is in `.gitignore`, so it is never committed.

### 3. Start the app

On start, the app creates or updates database tables automatically.

Make sure Docker Desktop is running (on Linux, the Docker service), then run:

```bash
docker compose up
```

This builds the app and starts it together with the database. The first run downloads images and takes a few minutes.

### 4. Open it in your browser

Go to <http://localhost:8000/health>. You should see:

```json
{ "status": "ok" }
```

### Stopping the app

Press `Ctrl+C` in the terminal where it is running, or run:

```bash
docker compose down
```

### After changing code

The app's code is copied into the image when it is built, so rebuild it to see your changes:

```bash
docker compose up --build
```

## Running tests

The app runs in Docker, but tests run on your own computer and connect to the database container. They use a separate test database, `osijek_test`, so they never touch your normal data.

### Prerequisites

You also need **Python 3.12 or newer**.

|         | Python                                                      |
| ------- | ----------------------------------------------------------- |
| Windows | [Install Python](https://www.python.org/downloads/windows/) |
| macOS   | [Install Python](https://www.python.org/downloads/macos/)   |
| Linux   | Usually already installed. Check with `python3 --version`.  |

On Linux, use `python3` wherever the commands below say `python`.

### 1. Create a virtual environment (once)

A virtual environment is a folder of Python libraries just for this project, so they don't mix with other projects on your computer. Create it in the project folder:

```bash
python -m venv .venv
```

Then activate it. Do this in every new terminal before running tests:

```bash
source .venv/bin/activate      # Linux and macOS
.venv\Scripts\activate         # Windows (PowerShell)
```

Your prompt now starts with `(.venv)`. `.venv` is in `.gitignore`, so it is never committed.

On Windows, if PowerShell refuses to run the script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

### 2. Install the libraries (once, and after `pyproject.toml` changes)

```bash
python -m pip install --upgrade pip
pip install -e .
pip install --group dev
```

The first line updates pip itself, because the last line needs pip 25.1 or newer. The second installs the app and the libraries it needs, listed in `pyproject.toml`. The third adds the tools only developers need, such as pytest.

### 3. Create the test database (once)

Start the database container, if it isn't running yet:

```bash
docker compose up -d postgis
```

Then create the test database inside it. Replace `<user>` with the `POSTGRES_ADMIN_USER` value from your `.env`:

```bash
docker compose exec postgis createdb -U <user> -T template_postgis osijek_test
```

`-T template_postgis` copies a template that has PostGIS turned on, which our location columns need. You don't need to create any tables: the tests do that themselves.

### 4. Run the tests

With the database container running and the virtual environment active, run this from the project folder:

```bash
pytest
```

You should see every test pass, for example `21 passed`. If a test fails, pytest shows which one and why.
