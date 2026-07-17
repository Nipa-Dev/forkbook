<h1 align="center">Forkbook</h1>

<p align="center">
  Self-hosted recipe and cooking notebook
</p>

## Quick Start with Podman

The easiest way to get started is using the `podman-compose.yaml`

1. Set up environment variables

Create a `.env` file in the project root:

Create a secret key: `openssl rand -hex 32`

```bash
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_DB=recipebook

SECRET_KEY="SECRET-KEY"
REFRESH_SECRET_KEY="ANOTHER-SECRET-KEY"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

EMAIL_BIDX_SECRET="YET-ANOTHER-SECRET-KEY"
```
2. Start the PostgreSQL database

```bash
podman compose up -d
```

3. Run the backend

```bash
cd backend
uv run run.py
```

The API will be available at `http://localhost:8000`

4. Install and run the frontend

```bash
cd frontend
pnpm install
pnpm run dev
```

The application will be available at `http://localhost:5173`

To create a new user, navigate to `http://localhost:5173/signup`

## Environment Variables

See `backend/app/utils/config.py` for additional configuration options.

## Development

### Formatting (Backend)

```bash
ruff format .
```

### Linting and Formatting (Frontend)

```bash
cd frontend
pnpm run lint
pnpm run format
```

## License

See LICENSE file for details.