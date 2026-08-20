# GOX Agent Teams Execution Bridge v1

This bridge turns the existing GOX Easy Jobs / Agent Teams design into a runnable, runtime-agnostic execution loop.

## What it does

1. Loads a bounded Easy Job JSON.
2. Loads an optional compiled Paper Stack context packet.
3. Builds one canonical prompt for the current cycle.
4. Runs an identical-agent ensemble in parallel.
5. Captures stdout/stderr and exit evidence per agent.
6. Writes a synthesis packet for the next judge/synthesizer cycle.
7. Persists status and run state under `.gox/runs/`.
8. Stops cleanly when the configured agent runtime is unavailable instead of pretending execution occurred.

## Runtime policy

The bridge does **not** guess the CLI syntax for Codex, Claude, Gemini, OpenCode, Herdr, or another runtime. Configure the exact executable and argument list in `execution_bridge/config.json` after verifying the installed CLI.

Example:

```json
{
  "runtime": {
    "executable": "codex",
    "args": [],
    "prompt_via_stdin": true
  },
  "limits": {
    "agent_timeout_seconds": 900,
    "max_parallel_agents": 3
  }
}
```

If the selected CLI requires a file path instead of stdin, use `{prompt_file}` inside `args` and set `prompt_via_stdin` to false.

## First checks on the VPS

From the GOX repository:

```bash
cp execution_bridge/config.example.json execution_bridge/config.json
python3 execution_bridge/bridge.py execution_bridge/job.example.json --config execution_bridge/config.json --probe
```

The probe reports the configured runtime plus any common CLIs it can actually find on PATH.

## Safe dry run

```bash
python3 execution_bridge/bridge.py execution_bridge/job.example.json --config execution_bridge/config.json --dry-run
```

This creates the canonical prompt and persistent job state but launches no agents.

## Real ensemble run

After the runtime configuration is verified:

```bash
python3 execution_bridge/bridge.py execution_bridge/job.example.json --config execution_bridge/config.json --ensemble 3
```

## Hidden gaps this v1 closes

- Runtime detection instead of assumed runtime availability.
- Canonical prompt compilation.
- Identical-agent parallel execution.
- Per-agent evidence capture.
- Timeouts and concurrency limits.
- Persistent run/job state.
- Deterministic prompt/job IDs.
- Failure-with-evidence behavior.
- Clean separation between executable work and Ron-only approval gates.

## Gaps intentionally left for the next bridge layer

- Automatic Paper Stack Compiler from Drive/repository sources.
- Model-specific adapter presets after the actual VPS CLI is verified.
- Synthesizer/Blind Judge automatic second pass.
- Automated repair recursion.
- Chrome approval bridge.
- Family-lane task routing and earnings ledger.
- Ready-to-work task-source connectors.
- VPS service supervision/restart recovery.

These should be layered on top of this bridge instead of being mixed into the first executable core.
