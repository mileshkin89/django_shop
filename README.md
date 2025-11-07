# django_shop

Shop on Django, DRF, Docker.

## Installation

Follow these steps to set up and run the application:

1.  **Install `uv`**: First, install the `uv` package manager using pip.
    ```bash
    pip install uv
    ```

2.  **Install dependencies**: Use `uv` to synchronize the project's dependencies based on `pyproject.toml` and `uv.lock`.
    ```bash
    uv sync
    ```

3.  **Configure environment variables**:
    - Copy `.env.sample` to `.env` and fill in the necessary information.
    - Copy `services/pgbouncer/.env.sample` to `services/pgbouncer/.env` and fill in the necessary information.

4.  **Build Docker containers**: This command builds the necessary Docker images for the application services.
    ```bash
    make build
    ```

5.  **Start all services**: This will start the Docker containers in detached mode.
    ```bash
    make up
    ```
    The application will be accessible at `http://localhost:8000/`.

6.  **Run Django migrations**: Apply database migrations to set up the database schema.
    ```bash
    make migrate
    ```

7.  **Seed the database with test data (Optional)**: Populate the database with sample users, catalog items, inventories, ratings, and favorites.
    ```bash
    make seed-all
    ```

8.  **Create a Django admin superuser (Optional)**: Create an admin user for the Django administration panel.
    ```bash
    make create-admin
    ```

## Development

-   **Stop all services**:
    ```bash
    make down
    ```

-   **Show container logs**:
    ```bash
    make logs
    ```

-   **Restart services (down, build, up)**:
    ```bash
    make restart
    ```

## Project Structure

-   `src/`: Contains the Django project and applications.
-   `docker-compose.yml`: Defines the services for Docker Compose.
-   `Dockerfile`: Dockerfile for the web service.
-   `Makefile`: Contains shortcuts for common development and deployment tasks.
