# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Install Poetry
RUN pip install poetry

# Install dependencies with Poetry
RUN poetry install --no-dev

# Expose FastAPI port
EXPOSE 8000

# Command to run FastAPI app using uvicorn
CMD ["poetry", "run", "uvicorn", "fastapi_assignment.main:app", "--host", "0.0.0.0", "--port", "8000"]
