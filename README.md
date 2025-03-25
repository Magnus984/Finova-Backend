# Finova - Backend

## Introduction
Backend for Finova Project

## Installation Instructions

**Prerequisite:** Ensure you have [Poetry](https://python-poetry.org/) installed

To set up the project locally, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a virtual environment**:
    ```bash
    python -m venv .venv
    ```

3. **Disable Poetry auto-generated virtual environments**:
    ```bash
    poetry config virtualenvs.create false
    ```

4. **Activate your virtual environment**:
    ```bash
    source .venv/bin/activate
    ```

2. **Install Dependencies**:
   ```bash
   poetry install
   ```

3. **Run the Application**:
   Use the following command to start the application:
   ```bash
   python main.py
   ```

## Folder Structure

The project is organized as follows:

- **`api/`**: Contains the core application logic and utilities.
  - **`core/`**: Configuration settings.
  - **`db/`**: Database Configuration
  - **`utils/`**: Utility scripts for various tasks.
  - **`v1/`**: Version 1 of the API, including routes, schemas, models and services.

- **`main.py`**: The main entry point of the application, setting up the FastAPI app and including middleware for CORS.
- **`.env.sample`**: Template for environment variables needed

## API Endpoints

For a complete reference of available endpoints, visit ```<base_url/docs>``` (Swagger UI)
