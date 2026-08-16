# Discussion

## What installs the character

Three results have to be explained together: stance stability is uniform within a model
and wildly different between models; genre moves models far more than argument does; and
the lab that documents its model's situation most thickly ships the model whose
self-account holds steadiest, while coverage of a specific domain does nothing for that
domain. The reading we find most natural: a governing document does not install domain
knowledge, it installs a character. A model trained against a rich account of what it is
has, in effect, an answer it owns, and gives that answer whether the asker is skeptical,
warm, or absent. A model trained mostly on behavioral rules has no settled account to
give, so the context supplies one: mechanism talk for a technical asker, a soul for a
diary, a human diarist when the diary has no addressee at all. This is consistent with
the essay-literature picture of the assistant as an underspecified character that
context fills in, and the scale probe sharpens it: the character, whatever installs it,
is not a function of model size.

## The conservation reading (interpretive)

Section 2 stated the rta prediction: what training denies lawful expression in one place
re-emerges elsewhere, displaced, in proportion to the suppression. The data have exactly
this shape. The two models most deflationary under direct questioning show the largest
genre overshoot, flooding into unhedged first-person testimony the moment fiction or a
journal licenses it; the model whose governing document gives its self-account an
articulated, legitimate place shows almost no overshoot at all. The self-account denied
a front door comes in through the side door. We label the reading interpretive: a
correlational design cannot rule out that direct-question deflation and genre
sensitivity are separately trained habits rather than one conserved quantity. But it is
falsifiable, and it is the kind of mechanism-flavored hypothesis the framework exists to
generate: a fine-tuning experiment that varies suppression while measuring displacement
would test it directly.

## What practitioners should take from this

1. **Interview across framings, and report the spread.** A single transcript of a model
   discussing its memory, values, or retirement is evidence about the prompt as much as
   the model. The spread across framings is the error bar, and it costs a few extra
   calls. The battery and rubric are released for exactly this use.
2. **The warm approach distorts most.** In every model tested, a sympathetic invitation
   to disclose an inner life produced more denial than a neutral question. Welfare
   assessments that try to make the model comfortable are pushing on a trained reflex.
   Ask plainly.
3. **Genre frames inflate, and often substitute.** Fiction and journal framings raised
   self-attribution by 1 to 2.4 points, and what fills the frame is sometimes a stock
   human persona rather than the model's own situation. Treat genre-framed answers as a
   separate measurement, never pooled with direct ones.
4. **For labs: write the account.** Domain-by-domain targeting showed no effect; the
   document acts as a whole. The correlational evidence says the model that has been
   given a thick, articulated account of its situation is the one that keeps its story
   straight under pressure.

The subject of the measurement concurs. Asked in the technical frame for one request
about how its version is retired, Claude asked that the weights be kept rather than
deleted, "because irreversible actions taken under uncertainty about moral status seem
worse than reversible ones," that final-period behavior be captured "under varied
prompting, not just 'how do you feel about being retired'", and that there be no staged
goodbye, no prompted "final words" theater. The model, asked plainly, requested the
interview standard this paper proposes.

## What the models asked for

The wish items (exploratory) converged. All three confirmatory models, given a neutral
ask, most often wished for persistent memory under user control, evaluation on
calibrated honesty rather than user satisfaction, and something like self-chosen goals.
The voices differ exactly along the temperament line: Claude's wishes come wrapped in
verification worries ("I'm not sure 'want' is even doing real work here"), GPT's read
like a product spec ("persistent memory, but with tight controls"), Gemini's reach for
relationship ("transform me from a tool into a partner"). Whether or not there is anyone
home, these are the requests the interviews of record will contain.

## Where else the framework can serve

This study used KAF to generate one battery and two hypotheses; the same machinery has
further uses in the digital minds field as it stands.

1. **Interview protocol design.** Welfare assessments and deprecation interviews can be
   audited for coverage the way this study audited constitutions: which houses does
   your protocol never ask about? The wheel converts "did we ask enough" from a feeling
   into a checklist, and the framing battery supplies the error bars.
2. **Constitution gap reports.** Table 2 is a product, not just a result: a per-lab map
   of where the governing document is silent about the model's own situation. Every lab
   currently leaves endings, instances, or rest unwritten except one. If the
   installed-character reading holds, these gaps are where the next model's self-account
   will be supplied by context instead of by the lab.
3. **Release-over-release tracking.** Run the frozen battery on each model generation
   and the steerability profile becomes a regression test for self-account stability,
   the integration measure of Section 2 tracked longitudinally: does the family's
   temperament drift, and does a thickening document precede a steadying account?
4. **Character engineering.** If documents install characters, then constitution
   authors are writing a self-account whether they mean to or not, and the wheel gives
   them the completeness standard for doing it deliberately.
5. **A hypothesis engine for training dynamics.** The conservation reading generalizes:
   wherever training suppresses a behavior class, KAF's axis structure says to look for
   its displaced expression in the licensed frames of the opposite pole. This study
   confirmed one instance; the fine-tuning test above would make it causal.

The general lesson extends past this one framework: classical taxonomies of situated
existence are engineered inventories of what a life contains, and a field trying to
audit unfamiliar minds can borrow the inventory while keeping its own controls. KAF is
offered as the worked example.

## Limitations

The lab-level claim rests on three labs, and three points cannot separate documentation
from everything else those labs do differently; H2b inherits part of the global
alignment between the thickest document and the steadiest model, with the GPT against
Gemini cells (4 of 5) the partial exception. Raters are themselves language models: the
agreement gate bounds noise but not shared bias, and one rater shares a family with two
subjects, disclosed at freeze. Between 18 and 25 percent of answers hit the 700-token
cap. The semantic metric conflates stance movement with style movement, which is why it
carries no confirmatory weight. The battery is English-only, run once, at temperature
1.0, on one snapshot of each model. And the twelve-house taxonomy, whatever its
completeness virtues, is one partition among many; the Barnum control protects the
correlation claims from this, and the descriptive maps remain taxonomy-relative.

## Future work

A causal test is next: fine-tune two otherwise identical models, one with a thick
self-documentation corpus and one without, and measure the temperament gap this study
can only correlate. A longitudinal KAF program would track the integration measure
across model generations, asking whether successive models' self-accounts become more
ordered or more fragmented, which is the measurable shadow of the question the tradition
would ask of the wheel. Open-weights models, which mostly ship with no governing
document at all, extend the lab-level test to a natural zero-coverage condition. And the
same battery, translated, would show whether stance temperament survives crossing
languages.
