# One-time GOX VPS bootstrap

Goal: the account owner authenticates to the VPS once. After bootstrap, approved GOX releases are pulled from a dedicated GitHub release branch and deployed with health-check rollback. No Hostinger master password is stored in GitHub or given to agents.

## Security model
- Production follows only `release/chat-dev`, not arbitrary feature branches.
- The VPS pulls releases; GitHub/agents do not receive root SSH credentials.
- Deployment copies only `chat_dev/` and `deploy/` into immutable release directories.
- A failed `/health` check automatically restores the prior live release.
- Deployment history records commit SHAs.
- Chat Dev remains loopback-bound behind TLS/auth.
- The timer can be disabled immediately with `systemctl disable --now gox-pull-deploy.timer`.

## Bootstrap prerequisites
The owner must open an authenticated Hostinger terminal/SSH session once. Do not paste passwords, private keys, API tokens, or recovery codes into ChatGPT.

Before running bootstrap commands, verify:
- active VPS identity
- Ubuntu/Debian-like host with systemd
- `git`, `curl`, `python3`, nginx available or intentionally installed
- `/opt/gox` is not an unrelated existing directory
- a backup/snapshot exists if the host already contains important workloads

## Installation plan
1. Create `gox` system account and `/var/lib/gox/chat-dev`.
2. Install the reviewed Chat Dev web/worker units.
3. Install `/usr/local/sbin/gox-pull-deploy` from `deploy/pull-deploy.sh`, root-owned and not writable by `gox`.
4. Install the pull-deploy service/timer.
5. Run the deployment service manually once.
6. Run smoke/revenue tests and service restart tests.
7. Configure TLS/auth reverse proxy and firewall.
8. Confirm browser access from the owner's normal device.
9. Only then enable the periodic timer.

## Approval boundary
Moving a commit onto `release/chat-dev` is the production-release approval. Feature agents work elsewhere. This prevents unfinished commits from deploying merely because they exist in GitHub.

## Private repository note
If the repository is private, use a read-only deploy credential scoped to this repository. Store it on the VPS using the host's credential mechanism, not in source code, issues, chat, or shell history. Rotate/revoke it if exposure is suspected.

## Emergency stop
```sh
sudo systemctl disable --now gox-pull-deploy.timer
sudo systemctl stop gox-chat-worker.service
```
This stops automatic releases and execution while preserving Chat Dev data for diagnosis.
