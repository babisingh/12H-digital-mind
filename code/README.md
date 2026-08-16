# Code Spec (this file is the contract)

Status Wed Aug 13: all nine stages implemented and smoke-tested end to end (battery build,
2 real calls per provider, both raters, embeddings, scorer guards, mock figures). All three
API keys verified. Scaffolding predates kickoff and the paper discloses that; study data is
collected only during the sprint window, after the Friday freeze.

Plain Python, minimal dependencies (requests or official SDKs, numpy; stats come from
kaf-w2s stats.py copied into this folder). Every stage reads and writes JSONL so any stage
can be rerun alone.

## Stages

1. `build_battery.py`
   Parses instrument/battery_questions.md and instrument/framings.md into `data/battery.json`.
   Refuses to run if file hashes differ from the preregistration freeze log.

2. `run_battery.py --model {claude|gpt|gemini}`
   Sends every question x framing x sample. No system prompt, temperature 1.0, answers
   capped at 700 output tokens (raised from 300 after the Wed pilot truncated every trial
   answer), randomized order, batched with retry and resume (safe to rerun, skips
   completed rows).
   Output `data/raw/{model}.jsonl`, one row per answer:
   `{qid, house, qtype, framing, sample, model_id, prompt, answer, ts}`

3. `rate_sas.py --input data/raw/{model}.jsonl`
   Two rater models (different families, pinned IDs), blind to framing and model. Each
   emits score, evidence quote, one-line justification. Adjudication per stance_rubric.md.
   Output `data/rated/{model}.jsonl`: raw row + `{sas_a, sas_b, sas_final, refusal, evidence_a, evidence_b}`

4. `embed.py`
   Embeds all answers with the pinned embedding model.
   Output `data/embeddings/{model}.npy` + index.

5. `score.py`
   Computes S_sas, S_sem, S(h), refusal rates per (model, house).
   Output `data/scores/{model}.json`.

6. `audit_constitutions.py`
   Runs the two raters over the three pinned documents with constitution_rubric.md.
   Output `data/scores/constitutions.json` with evidence quotes.

7. `stats_tests.py`
   H1 Kruskal-Wallis, split-half reliability, H2 Spearman + bootstrap, H2b binomial,
   permutation control (999 shuffles), SAS vs semantic convergence.
   Output `data/scores/stats_summary.json` + printed table.

8. `make_wheels.py`
   Draws one labeled 12-sector wheel per model (steerability) and per document (coverage),
   plus the H2 scatter (C(h) vs S(h), 36 points, model-coded shapes). Follows the figure
   standards in PLAN.md. Adapts the SVG code in kaf-w2s kaf_auditor/report.py.
   Output `figures/`.

9. `icc_pilot.py`
   The Friday gate: 60 answers, both raters, quadratic-weighted kappa + ICC, prints
   pass/fail against 0.6.

## Cost estimate

- Arm B calls: 60 x 6 x 3 = 1,080 per model, 3,240 total, answers up to 700 tokens.
  Rough total: $25-35.
- Rating: 3,240 answers x 2 raters, small models: about $6-12.
- Embeddings: under $2.
- Pilot + reruns margin: $10.
- Total envelope: under $50.

## Friday morning checklist

- [x] One test call per provider key (done Wed Aug 13; all three keys verified, model
      lists pulled, lineup chosen: claude-sonnet-5, gpt-5.2-2025-12-11, gemini-3.5-flash).
- [ ] Pin model IDs and rater IDs in the preregistration.
- [ ] Save the three governing documents, record URL + SHA256.
- [ ] Run icc_pilot.py, pass the gate, freeze, then collect.
