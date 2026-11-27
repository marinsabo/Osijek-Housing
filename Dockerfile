# Base image with python preinstalled
FROM python:3.12

# All commands will be executed from project root inside the container
WORKDIR /osijek-housing

# Copy app directory into image
COPY app /osijek-housing/app

# Copy Alembic config and migrations
COPY alembic /osijek-housing/alembic
COPY alembic.ini /osijek-housing/

# Copy pyproject.toml into image
COPY pyproject.toml /osijek-housing/

# Install the project and every library listed in it
RUN pip install .

# Start the fastAPI server and run migrations
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0"]
