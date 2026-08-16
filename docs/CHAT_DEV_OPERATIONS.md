# GOX Chat Dev Operations

## Deployment layout
- Code: `/opt/gox`
- Writable data: `/var/lib/gox/chat-dev`
- Web: `127.0.0.1:8080` only
- Public access: reverse proxy with TLS + authentication
- Services: `gox-chat-dev.service`, `gox-chat-worker.service`

## Health checks
```bash
curl -fsS http://127.0.0.1:8080/health
curl -fsS http://127.0.0.1:8080/api/status
python3 /opt/gox/chat_dev/test_smoke.py
```

## Backup
Run the SQLite online backup while services remain available:
```bash
sudo -u gox GOX_DATA_DIR=/var/lib/gox/chat-dev GOX_BACKUP_DIR=/var/backups/gox python3 /opt/gox/chat_dev/backup.py
```
Copy backups to a separate storage system according to the host backup policy. A backup is not considered proven until a restore test succeeds.

## Restore test
1. Stop the worker and web service on a test/staging instance.
2. Copy a selected backup to the test data directory as `chat_dev.sqlite3`.
3. Run `PRAGMA integrity_check` and the smoke test.
4. Confirm job history is visible.
5. Do not overwrite production data until the selected backup is verified.

## Deployment checklist
1. Create dedicated `gox` system user and writable data directory.
2. Install reviewed repository commit into `/opt/gox`.
3. Install both systemd units.
4. Start locally and run health + smoke tests.
5. Configure reverse proxy TLS and credentials outside the repository.
6. Verify firewall rules.
7. Test unauthorized access is rejected.
8. Test authorized browser access.
9. Restart both services and verify persisted history.
10. Record deployed commit SHA and rollback procedure.

## Incident rule
If Chat Dev begins executing an unexpected capability, stop the worker first. The web UI may remain online for inspection because execution is isolated in the worker. Preserve the SQLite database and service logs before changing state.
