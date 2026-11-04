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

Make sure Docker Desktop is running (on Linux, the Docker service), then run:

```bash
docker compose up
```

This builds the app and starts it together with the database. The first run downloads images and takes a few minutes.

### 4. Open it in your browser

Go to <http://localhost:8000>. You should see:

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
