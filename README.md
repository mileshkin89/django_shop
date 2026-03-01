# Django Shop

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
- Shopping cart, checkout flow, and Stripe payments
- User registration, authentication, and password reset
- Social login via OAuth 2.0 (Google, Facebook) with guest cart merging
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
| `.env.sample` | Main application (Django, DB, OAuth, etc.) |
| `services/pgbouncer/.env.sample` | PgBouncer connection pooler |

Copy each sample to `.env` (or `services/pgbouncer/.env`) and set values for your environment (e.g. `SECRET_KEY`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`).

### OAuth 2.0 (Social Login)

The application supports social authentication via Google and Facebook. To enable it, set the following variables in `.env`:

| Variable | Description |
|----------|-------------|
| `GOOGLE_CLIENT_ID` | Google OAuth 2.0 Client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 2.0 Client Secret |
| `FACEBOOK_CLIENT_ID` | Facebook OAuth App ID |
| `FACEBOOK_CLIENT_SECRET` | Facebook OAuth App Secret |

To obtain these credentials:

- **Google:** Create a project in [Google Cloud Console](https://console.cloud.google.com/), enable the Google+ API, and create OAuth 2.0 credentials. Add `http://localhost:8000/accounts/social/google/login/callback/` as an authorized redirect URI.
- **Facebook:** Create an app in [Meta for Developers](https://developers.facebook.com/), add Facebook Login, and configure `http://localhost:8000/accounts/social/facebook/login/callback/` as a valid redirect URI.

### Stripe (Payments)

The checkout flow uses [Stripe Checkout Sessions](https://docs.stripe.com/payments/checkout) for payment processing. Set the following variables in `.env`:

| Variable | Description |
|----------|-------------|
| `STRIPE_SECRET_KEY` | Stripe secret API key (starts with `sk_test_` or `sk_live_`) |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable API key (starts with `pk_test_` or `pk_live_`) |
| `STRIPE_WEBHOOK_SECRET` | Webhook signing secret (starts with `whsec_`) |

#### Obtaining Stripe API Keys

1. Create an account at [Stripe Dashboard](https://dashboard.stripe.com/).
2. Navigate to **Developers → API keys**.
3. Copy the **Publishable key** and **Secret key** (use test-mode keys for development).
4. Paste them into `.env` as `STRIPE_PUBLISHABLE_KEY` and `STRIPE_SECRET_KEY`.

#### Running the Stripe Webhook Locally

Stripe sends asynchronous events (e.g. `checkout.session.completed`) to your server via webhooks. During local development, use the [Stripe CLI](https://docs.stripe.com/stripe-cli) to forward events:

1. Install the Stripe CLI:

   ```bash
   # macOS
   brew install stripe/stripe-cli/stripe

   # Windows (scoop)
   scoop install stripe

   # Or download from https://docs.stripe.com/stripe-cli#install
   ```

2. Log in to your Stripe account:

   ```bash
   stripe login
   ```

3. Forward webhook events to your local server:

   ```bash
   stripe listen --forward-to localhost:8000/checkout/webhook/stripe/
   ```

4. The CLI will print a webhook signing secret (e.g. `whsec_...`). Copy it and set it as `STRIPE_WEBHOOK_SECRET` in `.env`.

5. Keep the `stripe listen` process running while testing payments.

> **Note:** In production, create a webhook endpoint in the Stripe Dashboard (**Developers → Webhooks**) pointing to `https://yourdomain.com/checkout/webhook/stripe/` and subscribe to the `checkout.session.completed` event.

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
- **Payments:** Stripe Checkout Sessions
- **Authentication:** django-allauth (email + OAuth 2.0 via Google, Facebook)
- **Database:** PostgreSQL 17 (with PgBouncer for connection pooling)
- **Package management:** uv, pyproject.toml
- **Containerization:** Docker, Docker Compose
- **Testing:** pytest, pytest-django

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.
