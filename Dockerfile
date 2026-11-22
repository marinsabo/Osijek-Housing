# Base image with python preinstalled
FROM python:3.12

# All commands will be executed from project root inside the container
WORKDIR /osijek-housing

# Install fastAPI and uvicorn packages
RUN pip install fastapi uvicorn

# Install SQLAlchemy
RUN pip install sqlalchemy

# Install Alembic and the Postgres driver (psycopg)
RUN pip install alembic "psycopg[binary]" python-dotenv

# Install GeoAlchemy2 (needed for location in database)
RUN pip install GeoAlchemy2

# Install Jinja2 (HTML templates) and python-multipart (reading HTML forms)
RUN pip install jinja2 python-multipart

# Copy app directory into image
COPY app /osijek-housing/app

# Copy Alembic config and migrations
COPY alembic /osijek-housing/alembic
COPY alembic.ini /osijek-housing/

# Start the fastAPI server and run migrations
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0"]