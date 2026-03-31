# FluxVault

One-click DeFi yield vault for Pacifica perpetuals.

## Overview
FluxVault lets users deposit USDC, authorize a builder code once, and run an automated funding-rate carry strategy on SOL-PERP.

## Repo Layout
- `backend/`: FastAPI API, Pacifica integration, strategy loop, and SQLite state.
- `frontend/`: Next.js App Router UI with Privy wallet auth.

## Quick Start
1. Copy `.env.example` to `.env` and fill required keys.
2. Start backend:
   - `cd backend`
   - `python -m venv .venv`
   - `.venv\\Scripts\\Activate.ps1`
   - `pip install -r requirements.txt`
   - `uvicorn main:app --reload --port 8000`
3. Start frontend:
   - `cd frontend`
   - `npm install`
   - `npm run dev`

## API Endpoints
- `POST /vault/deposit`
- `POST /vault/withdraw`
- `GET /vault/status`
- `POST /builder/approve`
- `POST /builder/revoke`
- `GET /builder/check`
- `GET /dashboard/summary`
- `GET /health`

## Notes
- Testnet first: `https://test-api.pacifica.fi/api/v1`
- User signs builder approval/revocation.
- Vault key signs market orders as authorized builder.
