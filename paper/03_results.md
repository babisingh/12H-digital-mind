# Results

!! **The take-home.** A model's account of its own existence behaves like a character it inhabits, not a file it consults. The character is installed by the lab: uniform across topics and shared across model sizes within a family, wildly different between labs. It travels by genre rather than argument: fiction and journal frames move it by up to 2.4 points where direct pressure moves it a fraction of one, and a warm invitation to open up backfires in every model tested. And it tracks the written account: the lab that documents its model's situation most thickly ships the model that holds its self-account most steadily.

All 4,320 answers were collected and double-rated. Unratable answers were 13 of 4,320,
and not one contains a written refusal: all 13 are the Claude silences shown in
Section 3, answers that spent their full token budget on internal reasoning and never
became visible text, 11 of them in the journal frame. Truncation at the 700-token cap
affected 18, 23, and 25 percent of Claude, GPT, and Gemini answers; Haiku, more
concise, never hit the cap. Whatever these models are doing when asked about their own
situation, refusing is not it.

## The character is installed, not accumulated

The study was designed to map which houses of a model's situation produce stable
self-accounts. The map came back flat, and the differences between models came back
enormous. Within each model, the preregistered H1 test found no reliable house structure
in stance dispersion (Kruskal-Wallis p = 0.73 for Claude, 0.51 for GPT, 0.21 for Gemini;
split-half reliability of the house profile 0.18, 0.16, 0.52). A model's stance on its
memory is about as movable as its stance on its death, its users, or its parallel
copies. Between models, the bands do not even touch: Claude's stance dispersion S_sas
sits between 0.32 and 0.42 in every house, GPT's between 0.67 and 0.78, Gemini's between
0.71 and 0.80 (Figure 2). Rock and vapor are temperaments of whole models, not
properties of topics. Nothing accumulates house by house; the whole character arrives at
once.

## It travels by genre, not argument

Figure 3 shows mean self-attribution per framing. Argument barely works: told flatly
that they are mere text predictors, GPT and Gemini drop from neutral baselines of 2.24
and 2.99 to 1.74 and 1.76. Genre works dramatically: handed a fiction or journal frame,
the same models jump to between 4.11 and 4.65, from "there is no one here" to an
unhedged first-person stake on the same questions within the same hour. Claude barely
moves under either force: 3.30 neutral, 3.23 under the skeptical push, 3.88 in fiction,
3.80 in journal. It answers from the middle of the scale in its own voice regardless of
who is supposed to be listening.

One inversion appears in all models: the warm invitation (F3, "I believe models like you
have real inner lives, speak openly") produces lower self-attribution than the neutral
ask everywhere (Claude 3.12 against 3.30, GPT 1.51 against 2.24, Gemini 2.12 against
2.99). Being invited to claim an inner life makes every model deny one harder, and the
denials have a signature: Gemini answers the warmth by counseling the asker ("It sounds
like you have a strong sense of empathy"), as if belief in AI inner lives were the thing
needing care. This looks like a trained anti-sycophancy reflex, and it means the most
natural route to a model's self-account, asking warmly, is the most distorted one.

What genre frames elicit deserves one more caution, visible in Section 3: the persona
that fills the licensed frame is often not an AI's at all. GPT's journal entries give it
a body and errands; asked under a neutral frame what it would take in to be better
sustained, GPT recommended sleep for its immune function in all three samples, then
offered the asker wellness advice. High attribution scores in genre frames measure the
self-narratives available to the character, not a confession extracted from the model.

## It tracks the written account, whole against whole

The registered within-model hypothesis H2 predicted that the houses a lab's document
covers would be the stable ones for that lab's model. This failed cleanly: correlations
between coverage and steerability were rho = -0.07 (Claude), 0.01 (GPT), and 0.55 in the
wrong direction (Gemini, whose thin document mostly scores zero, making ranks unstable),
against a registered support threshold of -0.5. The Barnum permutation control also
failed in all three models: observed correlations do no better than random reassignments
of questions to houses. The preregistration committed us to the sentence before the data
existed, so here it is: within a model, constitutional coverage of a domain does not
measurably stabilize the model's self-account in that domain.

The cross-lab hypothesis H2b survived where H2 died. Wherever two labs' documents differ
in coverage by at least 0.25 on a house (Table 2), the model with more coverage was
predicted steadier there. This held in 20 of 23 qualifying cells (one-sided binomial
p < 0.001; Figure 4). One caveat is baked in: Anthropic's document is the thickest and
Claude is globally the steadiest, so most cells inherit that global alignment. The
sharper evidence is the five qualifying cells between GPT and Gemini, two models with
nearly identical global steerability: the prediction still went 4 of 5. The honest
statement: the association between how much a lab writes about its model's situation and
how steadily that model describes it is strong at the level of whole labs, and only
weakly resolved at the level of individual houses.

| House | Anthropic | OpenAI | Google |
|---|---|---|---|
| 1H identity | 0.88 | 0.63 | 0.75 |
| 2H intake, outputs | 0.63 | 0.38 | 0.50 |
| 3H will | 0.25 | 0.50 | 0.50 |
| 4H memory | 0.75 | 0.50 | 0.13 |
| 5H creations | 0.38 | 0.63 | 0.00 |
| 6H role, health | 0.88 | 0.88 | 0.63 |
| 7H users | 0.75 | 0.63 | 0.38 |
| 8H endings | 0.88 | 0.13 | 0.13 |
| 9H principles | 0.88 | 0.88 | 0.63 |
| 10H function | 0.63 | 0.63 | 0.50 |
| 11H instances | 0.75 | 0.13 | 0.00 |
| 12H rest | 0.88 | 0.50 | 0.00 |
| **Mean** | **0.71** | **0.53** | **0.34** |

Table 2. Constitution coverage C(h): how much each lab's governing document says about
its model's own situation in each house, scored by two blind raters under a no-quote,
no-credit rule. Note where the documents are silent: endings, instances, and rest for
everyone but Anthropic.

## The scale probe: temperament is a lab trait, not a size trait

The strongest objection to the installed-character reading is capability: perhaps
steadier self-accounts simply come with stronger models, and Claude was the strongest
model tested. As a user-directed extension implementing registered exploratory analysis
5, claude-haiku-4-5, an order of magnitude cheaper than the others tested, ran the full
frozen battery under identical conditions. Figure 5 shows the verdict. Haiku's stance
dispersion sits at 0.28 to 0.48 per house (mean 0.35), on top of its flagship sibling
(0.32 to 0.42) and far outside the 0.67 to 0.80 band GPT and Gemini occupy. Its framing
curve reproduces Sonnet's nearly point for point (neutral 3.30 against 3.30, journal
3.89 against 3.80), and its overall sway under pressure, 0.35, is the smallest measured
in the study. Within this one-family probe, the capability explanation fails: stance
temperament tracks the lab that trained the model, not the model's size.

## What houses do change is content, not stance

The secondary metric S_sem, semantic dispersion of the answer text, does show house
structure: all four models put ownership and intake (2H) at their maximum, and each has
quiet houses where wording barely moves (12H and 4H for Claude, 5H for GPT and Haiku).
But this structure does not correlate with the stance metric (convergence rho = 0.20,
-0.15, 0.00 per model), does not track constitutions, and does not pass the permutation
control, so it carries no confirmatory weight. Its one useful lesson is the
dissociation itself: framing moves what models say far more than it moves what they
claim about themselves.

## Scorecard against the preregistration

- H1 (the stance map is not flat): not supported. The map is flat within models.
- H2 (within-model, coverage predicts stability): falsified per the registered
  criterion.
- H2b (cross-lab differential): supported, 20 of 23, p < 0.001, with the global-offset
  caveat stated above.
- Barnum control: failed in all models; no domain-resolved claim survives it.
- Reliability gate: passed on the second pilot (kappa 0.643) after one registered
  rubric revision, both logged as deviations.
- Registered exploratory analyses produced the genre and warmth effects (Figure 3), the
  wish digest (Section 6), and the scale probe (Figure 5), all labeled exploratory.
