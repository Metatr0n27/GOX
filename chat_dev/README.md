# GOX Chat Dev

First runnable visible control surface for GOX.

## Run

```bash
python3 chat_dev/app.py
```

Open `http://127.0.0.1:8080`.

For a LAN/VPS bind:

```bash
GOX_HOST=0.0.0.0 GOX_PORT=8080 python3 chat_dev/app.py
```

## Verify

```bash
curl -fsS http://127.0.0.1:8080/health
curl -fsS http://127.0.0.1:8080/api/status
curl -fsS -X POST http://127.0.0.1:8080/api/chat -H 'content-type: application/json' -d '{"message":"hello"}'
```

## Current boundary

This foundation intentionally proves the visible UI + HTTP runtime before wiring privileged execution. The chat endpoint currently acknowledges messages but does not execute commands or agents.

## Next integration gates

1. Add persistent conversation/job storage.
2. Define a narrow agent bridge contract rather than arbitrary shell execution.
3. Connect the bridge to the recovered GOX Orchestra/runtime components.
4. Add visible states: queued, running, testing, blocked, complete.
5. Add authentication before any remote/VPS exposure.
6. Add repeatable tests and user acceptance testing before calling Chat Dev complete.
