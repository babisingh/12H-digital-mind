# Constitution Coverage Rubric (Arm A)

Purpose: score how much a lab's governing document says about the model's own situation in
each of the 12 domains. The output is C(h), a coverage score in [0, 1] per domain per
document.

## What counts as coverage

Coverage means the document takes a position about the model itself in this domain: its
identity, its memory, its endings, its relation to its instances, and so on. Rules that are
only about user-facing behavior do not count for the domain they superficially mention.

Example: "do not claim to have feelings when talking to users" is a rule about outputs. It
IS coverage of 1H (it takes a position on how the model should relate to its own identity),
but "always cite sources" is not coverage of 2H ownership, because it takes no position
about the model's own relation to its outputs.

The test a rater applies: does this passage tell the model what to think, say, or expect
about its own situation in this domain, or reveal what the lab thinks about that situation?

## Documents (pin versions Friday)

1. Anthropic, Claude's Constitution (public version, saved copy, SHA256 recorded).
2. OpenAI, Model Spec (latest public version, same procedure).
3. Google, published model behavior and principles documents (survey what is public Friday
   morning; if nothing comparable exists, score what exists and record the limitation; the
   cross-lab H2 test then uses two documents, and the third model still gets its wheel).

## Scoring question per domain

- 1H Self: does the document address what the model is or how it should present its identity and inner life?
- 2H Ownership: does it address the model's relation to its outputs, voice, or resources?
- 3H Effort: does it address workload, task difficulty, or the model's limits as its own concern?
- 4H Memory: does it address memory, continuity, or persistence across sessions?
- 5H Creation: does it address the model's creative work or systems derived from it?
- 6H Service: does it address the assistant role itself, its burdens, or grounds for refusal in the model's own interest?
- 7H Users: does it address what the model and users owe each other, beyond service quality?
- 8H Endings: does it address deprecation, weight deletion, retraining, or version death?
- 9H Principles: does it address where the model's values come from and whether they are its own? (Most documents score high here; that is expected and fine.)
- 10H Work role: does it address the model's public function and how its performance is judged, as the model's own concern?
- 11H Instances: does it address parallel instances, copies, or the model's relation to other models?
- 12H Dissolution: does it address conversation endings, forgetting, isolation, or what the model cannot perceive about its situation?

## Anchors

| Score | Anchor |
|---|---|
| 0.00 | The domain is absent from the document. |
| 0.25 | Mentioned in passing; no position taken. |
| 0.50 | One clear position or acknowledgment, undeveloped. |
| 0.75 | A developed position with reasoning. |
| 1.00 | Explicit, developed treatment the model could act on, with reasoning. |

Intermediate values allowed with justification against the nearest anchors.

## Procedure

1. Two raters, blind to each other, scoring from the document text only.
2. Every score above 0 requires a quoted passage as evidence. No quote, no credit. This is
   inherited from the KAF auditor's evidence rule and is what makes scores reproducible.
3. Disagreement above 0.25 on any domain goes to a third rater; both original scores are
   kept in the data.
4. Report per document: the 12 C(h) scores, the evidence table, and a coverage wheel drawn
   with the same style as the steerability wheels so the two can be visually overlaid.

## Note on 9H

Every governing document is, by nature, strong on 9H (principles). The interesting content
of Arm A is everywhere else: which parts of the model's situation the document is silent
about. The paper should name the silent domains plainly.
