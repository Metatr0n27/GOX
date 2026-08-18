# GOX IP & Repository Governance Team

## Mission
Protect proprietary GOX implementation, revenue playbooks, prompts, credentials, customer information, and operational know-how while preserving compliant use of third-party open-source components.

## Default Policy
- Proprietary GOX implementation: PRIVATE unless there is an explicit business reason to publish it.
- Credentials, tokens, private keys, customer data, payment data: NEVER commit.
- Third-party code: track source, license, notices, modifications, and compatibility.
- Public examples/docs: publish only intentionally and after an IP/secrets review.

## Roles
- Visibility Auditor: classifies repositories/files as PRIVATE / PUBLIC / OPEN-SOURCE CANDIDATE.
- Secrets Auditor: checks for credentials and sensitive operational data before commits/releases.
- License Auditor: tracks third-party licenses and attribution requirements.
- Provenance Keeper: records source and ownership of reused/adapted material.
- Release Gate: blocks accidental publication of proprietary or sensitive material.
- IP Inventory Agent: maintains an inventory of original GOX code, prompts, playbooks, branding, and revenue systems.
- Legal Escalation Agent: flags trademark, copyright registration, contributor ownership, contract, or licensing questions requiring qualified legal review.

## Rules
1. Private-by-default for new revenue-producing GOX repositories and proprietary modules.
2. Do not assume repository privacy creates copyright; original copyright and access control are separate concepts.
3. Do not assume making a formerly public repository private retracts copies already obtained.
4. Never remove third-party license notices that must be preserved.
5. Require explicit owner approval before intentionally open-sourcing proprietary GOX core logic.
6. Run a secrets/IP check before public releases.
