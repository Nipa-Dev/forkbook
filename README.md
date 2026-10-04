<h1 align="center">Forkbook</h1>

<p align="center">
  Self-hosted recipe and cooking notebook
</p>

## Quick Start

1. Set up environment variables

Create a `.env` file in the project root:

```text
ALGORITHM=RS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EMAIL_BIDX_SECRET=change_me_email_bidx_secret

JWT_KID=dev-key-1

PRIVATE_KEY_PATH="./keys/private_key.pem"
PUBLIC_KEY_PATH="./keys/public_key.pem"
```

2. Run the backend

```bash
cd backend
uv run run.py
```

The API will be available at `http://localhost:8000`

3. Install and run the frontend

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

### Running tests in backend
```
uv run pytest
```

### Linting and Formatting (Frontend)

```bash
cd frontend
pnpm run lint
pnpm run format
```

## License

See LICENSE file for details.
