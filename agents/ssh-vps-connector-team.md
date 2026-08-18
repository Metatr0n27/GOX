# GOX SSH/VPS Connector Team

## Mission
Create and maintain a legitimate, persistent execution path from GOX to approved VPS infrastructure so server work can be delegated to agents instead of the owner.

## Roles
1. Connector Architect — chooses the best execution path: SSH, local worker, API, or provider connector.
2. SSH Engineer — configures normal key-based SSH using known_hosts verification and approved credentials.
3. VPS Worker Manager — installs and supervises the GOX worker process on the VPS.
4. Command Broker — receives approved operational tasks and routes them to the connector.
5. Health Agent — verifies connectivity, latency, disk, memory, service state, and worker heartbeat.
6. Deployment Agent — pulls approved GOX revisions, installs dependencies, restarts services, and verifies deployment.
7. Diagnostics Agent — captures stdout/stderr, exit codes, service logs, and failure summaries.
8. Recovery Agent — retries transient failures, repairs broken sessions/configuration where safe, and restores last known-good state when needed.
9. Evidence Agent — records what command/action ran, when, on which host, and the verified result.
10. Owner-Action Reducer — escalates only the smallest unavoidable account-holder step.

## Execution Flow
GOX TASK -> COMMAND BROKER -> SSH/VPS CONNECTOR -> VPS WORKER -> VERIFY RESULT -> LOG EVIDENCE -> RETURN RESULT

## Rules
- Use only infrastructure the owner is authorized to administer.
- Prefer key-based SSH or provider-supported APIs.
- Never disable host-key verification as a shortcut.
- Never store private keys or passwords in Git.
- Runtime credentials come from environment variables or local secret stores.
- Every remote action must return exit status, stdout/stderr summary, and verification evidence.
- Destructive actions require explicit routing/approval unless a previously approved rollback rule applies.
- One failed VPS action must not stop unrelated revenue job cells.

## Done Definition
The connector team is VERIFIED when GOX can: connect to the VPS, run a harmless health command, deploy a known GOX revision, restart a GOX service, retrieve logs, detect a simulated failure, and recover or escalate with evidence.
