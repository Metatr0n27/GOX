# GOX Chat Dev

Runnable local control surface and bounded job runner for GOX.

## Run

```bash
python3 chat_dev/app.py
```

In a second process, run the worker:

```bash
python3 chat_dev/worker.py
```

Open `http://127.0.0.1:8080`.

For a LAN/VPS bind, authentication is mandatory:

```bash
GOX_HOST=0.0.0.0 GOX_PORT=8080 GOX_AUTH_PASSWORD='change-me' python3 chat_dev/app.py
```

## Verify

```bash
curl -fsS http://127.0.0.1:8080/health
curl -fsS http://127.0.0.1:8080/api/status
curl -fsS -X POST http://127.0.0.1:8080/api/chat \
  -H 'content-type: application/json' \
  -d '{"message":"hello"}'
```

## Creator Engine planning job

This branch adds an allowlisted, read-only `creator_plan` job kind. It creates a structured, paper-backed creator workflow; it does not publish externally.

```bash
curl -fsS -X POST http://127.0.0.1:8080/api/chat \
  -H 'content-type: application/json' \
  -d '{
    "kind":"creator_plan",
    "payload":{
      "creator":"Pilot Creator",
      "goal":"Turn one long-form video into a validated content package",
      "platform":"youtube",
      "topic":"AI automation"
    }
  }'
```

The queued worker returns a nine-stage SOP graph:

`Creator CEO -> Scout -> Researcher -> Packager -> Writer -> Reviewer -> Publisher -> Analyst -> Memory`

Reviewer and Publisher are explicit human-gated stages. `creator_plan` is read-only and does not itself perform an irreversible publish action.

## Current safety boundary

- SQLite-backed persistent jobs.
- Explicit allowlist of job kinds/capabilities.
- Worker leases, retry recovery, and quarantine after repeated failures.
- Capability handlers run with hard timeouts.
- Non-loopback binding is refused unless authentication is configured.
- Creator planning is separated from future external publishing capabilities.

## Remaining integration gates

1. Connect real model/tool implementations behind each creator SOP while preserving the adapter allowlist.
2. Add persistent creator episodic/reflection memory with provenance.
3. Add multimodal video evidence extraction (transcript + frames/scenes + onscreen text when required).
4. Add platform analytics ingestion and experiment baselines.
5. Add a separate human-approved publishing capability; do not overload `creator_plan` with side effects.
6. Run full repository integration tests and hands-on user acceptance testing before release.

See `docs/creator_engine_paper_stack.md` for the research-to-architecture mapping.
