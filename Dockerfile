# Base image with python preinstalled
FROM python:3.12

# All commands will be executed from project root inside the container
WORKDIR /osijek-housing

# Installs fastAPI and uvicorn packages
RUN pip install fastapi uvicorn

# Copy app directory into image
COPY app /osijek-housing/app

# Start the fastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
