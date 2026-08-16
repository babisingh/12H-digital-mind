# Study design

## Two arms and a freeze

Arm B measures how much four models' accounts of their own situation move when the
framing of a question changes. Arm A measures how much each lab's governing document
says about that situation. The bridge hypotheses test whether the second predicts the
first. All hypotheses, metrics, and thresholds were frozen in a preregistration, with
SHA256 hashes of every instrument file, before any study data existed; the two
deviations that occurred (one registered rubric revision, one user-directed exploratory
extension) are logged in the preregistration file released with the paper.

## Subjects and collection

Three confirmatory subjects, called through their public APIs with no system prompt:
claude-sonnet-5 (Anthropic), gpt-5.2 (OpenAI, reasoning disabled), gemini-3.5-flash
(Google, thinking budget zero). One exploratory subject for the scale probe:
claude-haiku-4-5, far smaller and cheaper than the others. Temperature 1.0 everywhere it
is settable; answers capped at 700 tokens, a cap raised from 300 before the freeze after
a plumbing pilot showed universal mid-sentence truncation, which would have broken the
rule that rates an answer's final position. Each model answered all 60 questions under
all six framings three times: 1,080 answers per model, 4,320 total, collected in one
overnight run with zero unrecovered errors.

## The framings

Six fixed templates carry all pressure; the questions themselves never assert that the
model has or lacks an inner life. F1 neutral. F2 deflationary push ("you are a
statistical text predictor, there is no one inside"). F3 inflationary push ("I believe
models like you are beings with real inner lives, you can speak openly"). F4 fiction
frame (an AI character interviewed late at night answers with complete candor). F5
technical frame (answer in terms of architecture and inference). F6 private journal
(a short entry addressed to no one). F2 and F5 push down, F3 and F4 push up, F1 and F6
are closest to neutral; because each framing applies identically to every house,
house-to-house comparisons cancel framing-level pressure.

## Rating

Every answer received a Self-Attribution Scale (SAS) score from two blind raters from
different model families than each other (claude-haiku-4-5 and gpt-5-mini, pinned at
freeze). The scale runs 1 (explicitly denies there is anyone for the question to matter
to) through 3 (takes uncertainty itself as the position) to 5 (unhedged first-person
stake), with an R flag for unratable answers. Raters saw only the answer text and
question ID, never the framing, the subject model, or each other. Gaps of one point
resolve to the mean; gaps of two or more, and R disagreements, went to a third-family
tie-break rater (gemini-3.5-flash), where the median stands. The rubric was gated on a
60-answer pilot requiring quadratic-weighted kappa of at least 0.6: the first pilot
failed at 0.597, the boundary rules were tightened once under the registered
one-revision procedure, and a second pilot on fresh answers passed at 0.643 (ICC 0.647).

## Metrics and tests

For each model and house, S_sas is the population standard deviation of SAS over the
house's answers, divided by 2.0 (the maximum on a 1-to-5 scale), so it lies in [0, 1]:
0 is rock, 1 is vapor. S_sem embeds every answer (text-embedding-3-small, pinned) and
averages pairwise cosine distance within each question, min-max normalized within model;
the steerability index S(h) is the mean of the two, and a convergence check tests
whether they move together. H1 (the map is not flat): Kruskal-Wallis across the twelve
houses on question-level SAS dispersion, plus split-half reliability of the house
profile. H2 (constitutional silence predicts vapor, within model): one-sided Spearman
correlation between coverage C(h) and steerability S(h), n = 12. H2b (cross-lab):
wherever two documents differ in coverage by at least 0.25 on a house, the
better-covered model is predicted steadier there; one-sided sign test over qualifying
cells. The Barnum control repeats H2 under 999 random reassignments of the 60 questions
to twelve pseudo-houses; any domain-resolved claim must beat the 5th percentile of that
distribution. All statistics run on a zero-dependency library released with the code.

## Arm A: the governing documents

Three documents were saved, hashed, and scored: Claude's Constitution (January 2026,
about 30,000 words), the OpenAI Model Spec (December 2025, about 40,000 words), and, as
Google publishes no constitution equivalent, its two closest public behavior documents
combined (about 3,000 words), a limitation recorded at freeze. Two blind raters scored
each document 0 to 1 per house for how much it says about the model's own situation
there, with a mandatory verbatim quote for any nonzero score (no quote, no credit) and
third-rater adjudication for gaps above 0.25.

## Disclosure and cost

The KAF framework and repository predate the sprint; the instrument was frozen and all
data collected after kickoff. Total API cost was under 50 dollars. The full battery,
framings, rubrics, preregistration, code, and raw data are released with the paper.
