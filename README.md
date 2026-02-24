# Django Shop

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-5.2+-green.svg)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

E-commerce web application built with Django, Django REST Framework, and Docker. Includes catalog, cart, checkout, user accounts, and admin tooling.

---

## Table of Contents

- [Description](#description)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development](#development)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)

---

## Description

Django Shop is a full-stack online store that provides:

- Product catalog with categories and search
- Shopping cart and checkout flow
- User registration, authentication, and password reset
- Django admin for content and order management
- REST API (DRF) for integration
- Docker-based deployment with PostgreSQL and PgBouncer

---

## Requirements

- [Python](https://www.python.org/) 3.13+
- [Docker](https://www.docker.com/) and Docker Compose
- [uv](https://github.com/astral-sh/uv) (recommended) or pip for local dependency management
- [GNU Make](https://www.gnu.org/software/make/) (optional, for `make` targets)

---

## Installation

1. **Clone the repository** (if not already):

   ```bash
   git clone <repository-url>
   cd django_shop
   ```

2. **Install `uv`** (recommended package manager):

   ```bash
   pip install uv
   ```

3. **Install project dependencies** (for local development without Docker):

   ```bash
   uv sync
   ```

   Dependencies are defined in `pyproject.toml` and locked in `uv.lock`.

4. **Configure environment variables** (see [Configuration](#configuration)).

5. **Build Docker images**:

   ```bash
   make build
   ```

6. **Start services**:

   ```bash
   make up
   ```

   The application is available at **http://localhost:8000/**.

7. **Apply database migrations**:

   ```bash
   make migrate
   ```

8. **(Optional) Seed the database** with sample users, catalog, inventories, ratings, and favorites:

   ```bash
   make seed-all
   ```

9. **(Optional) Create a Django superuser** for the admin panel:

   ```bash
   make create-admin
   ```

---

## Configuration

Environment variables are loaded from `.env`. Use the samples as templates:

| File | Purpose |
|------|--------|
| `.env.sample` | Main application (Django, DB, etc.) |
| `services/pgbouncer/.env.sample` | PgBouncer connection pooler |

Copy each sample to `.env` (or `services/pgbouncer/.env`) and set values for your environment (e.g. `SECRET_KEY`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`).

---

## Usage

- **Web UI:** Open http://localhost:8000/ in a browser.
- **Admin:** http://localhost:8000/admin/ (requires a superuser from `make create-admin`).
- **API:** REST endpoints are available under the configured API base path (see project URLs).

---

## Development

| Command | Description |
|--------|-------------|
| `make help` | List all available Make targets |
| `make up` | Start all services (detached) |
| `make down` | Stop all services |
| `make logs` | Stream container logs |
| `make restart` | Stop, rebuild, and start services |
| `make migrate` | Run Django migrations |
| `make seed-all` | Seed database with test data |
| `make create-admin` | Create Django superuser |
| `make clean-all` | Remove all seeded test data |
| `make test` | Run the test suite in Docker |

---

## Testing

Run the full test suite (starts DB, runs tests, stops DB):

```bash
make test
```

Tests are executed inside the `web` container with a temporary database. For local pytest runs without Docker, ensure the database is available and use:

```bash
uv run pytest
```

---

## Project Structure

```
django_shop/
├── src/                    # Django project and apps
│   ├── apps/               # Application modules (catalog, cart, accounts, etc.)
│   ├── static/             # Static assets (CSS, JS, images)
│   ├── templates/          # HTML templates
│   └── ...
├── services/
│   └── pgbouncer/          # PgBouncer service and config
├── docker-compose.yml      # Service definitions
├── Dockerfile              # Web service image
├── Makefile                # Development and deployment shortcuts
├── pyproject.toml          # Python project and dependencies
└── uv.lock                 # Locked dependency versions
```

---

## Tech Stack

- **Backend:** Django 5.2+, Django REST Framework
- **Database:** PostgreSQL 17 (with PgBouncer for connection pooling)
- **Package management:** uv, pyproject.toml
- **Containerization:** Docker, Docker Compose
- **Testing:** pytest, pytest-django

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.
