# Merchant Operations Dashboard (Phase 7)

## Overview

The Merchant Operations Dashboard provides the human-in-the-loop (HITL) approval layer for the RecoverAI platform. It acts as the final gatekeeper between the AI's autonomous recovery recommendations and actual simulated recovery execution.

## Key Features

1.  **Approval Gate**: All AI recommendations default to `pending_approval`. A human operator must explicitly approve or reject the action before the Executor can process it.
2.  **Dashboard UI**: A Next.js-based interface (`/dashboard`) that displays key recovery metrics, including total amount at risk, recovered amount, and recovery rate.
3.  **Case Management**: A detailed view for each recovery case (`/recovery/[id]`), showing the AI's diagnosis, confidence, recommended action, and providing action buttons (Approve/Reject).
4.  **Strict State Machine**: The lifecycle of a recovery case is tightly controlled via `state_machine.py`. A case can only move to `executing` if it is explicitly `approved`.

## Architecture & Flow

1.  **AI Agent (Phase 5)**: Diagnoses the failed payment and generates a recommendation.
2.  **State Machine (Phase 7)**: Transitions the case to `pending_approval`.
3.  **Dashboard API (Phase 7)**: Serves case details and metrics to the frontend.
4.  **Operator Action (Phase 7)**: A human reviews the case on the frontend and clicks Approve or Reject.
5.  **Approval API (Phase 7)**: Transitions the case to `approved` (or `rejected`).
6.  **Executor (Phase 6)**: Polls for `approved` cases, transitions them to `executing`, runs the simulation, and finally transitions them to `recovered` or `failed`.

## API Endpoints

*   `GET /api/v1/dashboard/metrics`: Retrieves aggregated metrics for the dashboard overview.
*   `GET /api/v1/dashboard/cases`: Retrieves a list of recovery cases with pagination and status filtering.
*   `POST /api/v1/recovery/{id}/approve`: Approves a pending recovery case. Requires `{ "approved_by": "operator_name", "reason": "optional" }`.
*   `POST /api/v1/recovery/{id}/reject`: Rejects a pending recovery case. Requires `{ "rejected_by": "operator_name", "reason": "required" }`.

## Testing

The Phase 7 implementation is covered by a robust suite of tests:
*   `tests/approval/test_approval_api.py`: Validates the approval/rejection logic and idempotency.
*   `tests/dashboard/test_dashboard_api.py`: Validates the dashboard metrics and case listing endpoints.
*   `tests/recovery/test_executor.py`: Updated to ensure the executor strictly requires the `approved` state before execution.
*   All existing Phase 1-6 tests (ML, Agent, Simulator) continue to pass.

## Running the Dashboard

1.  Start the backend and database via Docker Compose: `docker compose up -d`
2.  Start the Next.js frontend (requires Node.js):
    ```bash
    cd frontend
    npm run dev
    ```
3.  Navigate to `http://localhost:3000/dashboard` in your browser.
