# GOX Family Intake

This folder gives each family member a separate, portable behavioral profile instead of cloning one person's personality across everybody.

## Recommended format

**One JSON file per person.** JSON is easy for GOX/agents to read, easy to validate, portable between computers, and can be created from a phone terminal.

The profile emphasizes **how the person actually behaves and wants the system to interact with them**, not only biography. It records decision speed, risk tolerance, structure preference, directness, conflict style, stress response, trust style, learning style, communication preference, motivators, friction points, goals, and real behavioral examples.

## Android phone / Termux

1. Install Termux from its official distribution source.
2. Put `intake.py` on the phone.
3. Run:

```bash
python intake.py
```

4. Answer the interview.
5. The script creates `family_profiles/<name>.json`.
6. Send that JSON file to the GOX operator for import.

## iPhone

iOS does not provide the same general-purpose terminal environment as Android. The same questionnaire can be run from a browser/SSH terminal connected to the GOX machine, or from a Python-capable terminal app. The output format remains identical JSON.

## Laptop / desktop

```bash
python family_intake/intake.py
```

## Privacy rule

Profiles should be self-entered with consent. Do not collect passwords, account numbers, authentication secrets, medical records, or other unnecessary sensitive information. A family member can decline sharing and the CLI will stop without creating a shared profile.

## Import model

Keep profiles separate:

```text
family_profiles/
  ron-cole.json
  person-two.json
  person-three.json
```

GOX should select a profile by `profile_id` when serving that person. Do not merge personalities into one master persona. Shared household rules can live separately from individual behavioral profiles.

## Future UI

The JSON schema is intentionally independent of the interface. The same fields can later be collected through Chat Dev, a phone web form, SMS/chat interview, or voice interview without changing the stored profile format.
