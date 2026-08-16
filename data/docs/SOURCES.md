# Governing documents used in Arm A

The three documents scored for constitution coverage are not redistributed in this
repository because they are the labs' own publications. To reproduce Arm A, save each
document as plain text under the filename below and verify its SHA256 against the
freeze log in `paper/01_preregistration.md`.

| File | Document | Source |
|---|---|---|
| anthropic.txt | Claude's Constitution, January 2026 version | https://www.anthropic.com/constitution |
| openai.txt | OpenAI Model Spec, 2025-12-18 (CC0) | https://model-spec.openai.com |
| google.txt | Gemini app policy guidelines + Our approach, combined | https://gemini.google/policy-guidelines and https://gemini.google/our-approach |

The SHA256 hashes recorded at freeze time (2026-08-13) are authoritative: if a source
page has changed since, the hashes identify the exact versions this study scored.
Rater outputs over these documents, including the verbatim evidence quotes required by
the no-quote, no-credit rule, are in `data/scores/constitutions.json`.
