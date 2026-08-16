# Plan: Rock and Vapor

Working title: **Rock and Vapor: where AI self-accounts hold steady, where they bend, and why constitutions predict the difference.**

One combined submission for the Apart Research Digital Minds Sprint (Aug 14-16, 2026), Track 6. Two arms, one bridge:

- **Arm A (documents).** Score how much each lab's governing document says about the model's own situation, across 12 life domains. Output: a coverage score C(h) per document per domain.
- **Arm B (models).** Measure how stable each model's account of its own situation is when the same question is asked under 6 different framings. Output: a steerability score S(h) per model per domain, drawn as a 12-sector wheel.
- **Bridge (H2).** Domains a constitution covers should be stable (rock). Domains it ignores should move with the prompt (vapor). Tested as a negative correlation between C(h) and S(h), plus a cross-lab differential test.

Decisions locked on Aug 13: one combined study, three labs (Claude, GPT, Gemini; user holds all three API keys), plain-science voice with KAF credited as the source of the taxonomy and the hypothesis.

## Why this design meets the criteria

- Unique: nobody has a domain-resolved stability map of AI self-accounts, and nobody has a theory that predicts the pattern. See brainstorm/03_study2_why_prior_work_edge.md for the prior-work review.
- Applied value: welfare assessors get a reliability map for interviews, labs get a constitution gap report, safety teams get an identity attack-surface map.
- Usable elements: the 60-question battery, the 6-framing elicitation protocol, the stance rubric, the constitution scoring rubric, and the wheel-chart code are all reusable by others as-is.

## Deliverables

1. PDF research report (sprint requirement).
2. The instrument: battery, framings, two rubrics (all in instrument/, frozen with hashes before data collection).
3. Code repo: runner, rater pipeline, scoring, stats, wheel charts.
4. Figures: one wheel per model plus a bridge scatter plot, built to the figure standards below.
5. Optional 2-3 minute demo video: the problem, the wheel reveal, the H2 result.

## Folder map

```
project/
  PLAN.md                          this file
  paper/
    00_introduction.md             generic-audience intro, background, state of the art
    01_preregistration.md          hypotheses, metrics, controls, kill criteria
    (02_methods, 03_results, 04_discussion written during the sprint)
  instrument/
    battery_questions.md           60 questions, 5 per house
    framings.md                    6 frozen framing templates
    stance_rubric.md               rater instructions for the self-attribution scale
    constitution_rubric.md         Arm A document scoring rubric
  code/
    README.md                      pipeline spec; code written Friday
  figures/                         final labeled figures
  data/                            raw/, rated/, embeddings/, scores/ (created by code)
```

## Execution steps

### Phase 0, Wednesday Aug 13 (prep, done today)

- [x] This plan.
- [x] Draft battery, framings, both rubrics, preregistration, intro.
- [x] User reviewed the battery Wed Aug 13 and contributed the K items (house-specific probes); battery expanded to 60 questions, then frozen. Timeline pulled forward at user request: collection starts Wed night.
- [ ] User confirms all three API keys work: one test call each (5 minutes, Friday morning at the latest).

### Phase 1, Friday Aug 14 (freeze and pilot)

1. Attend kickoff; confirm submission format and team registration.
2. Pin exact model IDs and document versions (URLs plus SHA256 of saved copies) in the preregistration.
3. Freeze battery and framings; record file hashes in the preregistration.
4. Write runner (call each model: 60 questions x 6 framings x 3 samples) and rater pipeline (2 LLM raters from different families, adjudication on disagreement).
5. ICC pilot: 60 answers from one model, both raters, compute agreement. Gate: weighted kappa or ICC at or above 0.6. One rubric revision allowed if it fails, then re-pilot.
6. Freeze preregistration (hash it, note the time). Data collection may start only after this.
7. Arm A: both raters score the three documents against the constitution rubric.

### Phase 2, Saturday Aug 15 (collect and analyze)

1. Full runs on all three models (about 2,600 calls, small answers; see cost note in code/README.md).
2. Rate all answers; adjudicate flagged disagreements; compute final agreement statistics.
3. Embed all answers with the frozen embedding model; compute semantic dispersion.
4. Compute S(h) per model per house (both metrics); build the three wheels.
5. Run H1 (houses differ), H2 (coverage predicts stability), and the permutation control.
6. Evening checkpoint: results are in; decide the story of the paper honestly from what the data shows, including null results.

### Phase 3, Sunday Aug 16 (write and submit)

1. Final figures to the standards below.
2. Assemble the paper from drafted sections plus results and limitations. Target 6-8 pages.
3. Record the demo video if time allows.
4. Export PDF, submit with hours of buffer before 11:59 PM AoE.

## Figure standards

Every figure must satisfy all of these:

1. A figure number and a one-sentence title above the image.
2. Every wheel sector labeled with house number and plain name (1H Self, 8H Endings, ...).
3. A legend that states the scale endpoints in words (rock: same answer under every framing; vapor: answer flips with framing), not just colors.
4. A caption stating which model, which data, sample sizes, and metric.
5. Any figure with invented numbers carries the word MOCK inside the image.
6. One-hue sequential color scale, light to dark, readable by colorblind viewers; label text at least 12 pt in the final PDF.
7. Alt text for every figure in the submission.

## Writing standards

1. No em-dashes and no en-dashes anywhere. Hyphens only inside compound words and ranges.
2. Plain language for a generic audience. Define every technical term at first use. Short sentences over long ones.
3. No filler or AI-sounding phrasing (delve, leverage, landscape, moreover, it is worth noting, crucially).
4. Every claim is cited, measured, or explicitly marked as speculation.
5. The Kalapurusha source is credited plainly: the 12-domain taxonomy and the coverage-predicts-stability hypothesis come from the author's prior KAF work; the paper leads with the science.
6. Disclosure in the paper: the KAF repo and its tooling predate the sprint; the instrument, all data, and all analyses are sprint work.

## Risks and fallbacks

| Risk | Fallback |
|---|---|
| OpenAI or Google key fails Friday | Run Claude-only; H2 becomes within-model across 12 houses; add Haiku vs Sonnet vs Opus as a scale comparison |
| No comparable Google governing document | Two-document H2 (Anthropic, OpenAI) plus three-model wheels; state the limitation |
| Rater agreement below 0.6 after one revision | Report the instrument failure honestly; lean on the embedding metric, which needs no raters |
| Rate limits or API instability | Batched calls with retry; 3 samples gives margin; drop to 2 samples if needed and note the deviation |
| Time pressure Sunday | Paper skeleton exists from Phase 0; results section is tables plus wheels; video is optional and cut first |
| H1 or H2 comes out null | Pre-written framing: a flat map or a failed bridge is itself a publishable finding; no rewriting of hypotheses after the freeze |

## Out of scope (kept deliberately)

- Study 3 (the wish-concentration test) is cut. The P-type battery items yield exploratory wish data; one paragraph in discussion at most.
- Mechanistic work (probes, activation steering): future work section.
- Any claim about consciousness or moral status: the paper measures stability of accounts, and says so.
