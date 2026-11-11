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

# Copy app directory into image
COPY app /osijek-housing/app

# Start the fastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
