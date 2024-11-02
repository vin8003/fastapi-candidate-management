# FastAPI Candidate Management API

## Overview
The FastAPI Candidate Management API is a robust backend service designed for managing candidate data, complete with JWT-based authentication, email verification, and task processing using Celery and Redis. The application integrates Sentry for error tracking and observability.

## Features
- **User Registration and Authentication**: Secure user registration with password hashing and JWT-based authentication.
- **Candidate Management**: CRUD operations for candidate profiles.
- **Email Service**: Automated email verification and report delivery.
- **Background Task Processing**: Asynchronous report generation and email sending with Celery and Redis.
- **Error Monitoring**: Integration with Sentry for error tracking and monitoring.
- **Pre-Commit Hooks**: Linting and formatting checks using pre-commit hooks to ensure code quality.

## Tech Stack
- **FastAPI**: High-performance web framework for building APIs.
- **MongoDB**: NoSQL database for storing candidate and user data.
- **Redis**: In-memory data structure store used as a message broker for Celery.
- **Celery**: Distributed task queue for handling background jobs.
- **Sentry**: Error tracking and performance monitoring tool.
- **Docker**: Containerization for easy deployment and scalability.

## Prerequisites
- **Python 3.9 or higher**
- **Docker**
- **Poetry** for dependency management

## Installation

### Clone the Repository
bash
git clone git@github.com:vin8003/fastapi-candidate-management.git
cd fastapi-candidate-management

### Setup Environment Variables

Create a .env file from sample .env_copy file in the project root and configure the environment variables

### Install Dependencies

poetry install
Run the Application Locally

poetry run uvicorn fastapi_assignment.main:app --reload
## Run with Docker
Ensure Docker is installed, then run:


docker-compose up --build

## Running Tests

Running Tests Locally
Run the tests using pytest:


pytest tests
or
docker-compose run test_runner

## Usage

Access the API documentation at http://localhost:8000/docs when running locally.
Register a user, verify the email, and access secured endpoints with the JWT token.

## Contributing

Contributions are welcome! Please follow the pre-commit hooks for linting and formatting checks:


pre-commit install

## License

This project is licensed under the MIT License. See the LICENSE file for details.
