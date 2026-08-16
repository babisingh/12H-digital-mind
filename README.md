# Twelve Houses of a Digital Mind

Rock, vapor, and silence in AI self-accounts: a preregistered stability audit with the
Kalapurusha Alignment Framework (KAF).

Study developed for Apart Research Digital Minds Sprint, August 2026 (Track 6). 
Author: Babita Singh, PhD, Genethropic. 


Sixty questions covering the twelve Kalapurusha houses of a model's situation, each
asked under six framings, three times, of four models from three labs: 4,320 answers,
scored blind by two reliability-gated raters, beside an audit of how much each lab's
governing document says about its model's own situation. All hypotheses and instruments
were frozen, with SHA256 hashes, before any data existed.

Headline results: stance stability is a property of labs, not topics or model sizes;
fiction and journal frames move self-accounts far more than direct argument, and a warm
invitation to open up backfires in every model tested; thicker lab self-documentation
tracks steadier model self-accounts in 20 of 23 registered cross-lab comparisons
(p < 0.001).

## Layout

- `paper/` paper sections and the frozen preregistration with hashes and deviations log
- `instrument/` battery, framings, and rubrics. Byte-frozen: hashes in the
  preregistration verify against these files as shipped, so do not edit them
- `code/` full pipeline, plain Python 3, no external dependencies
- `data/` raw answers, blind ratings, embeddings, scores, pilots (`data/docs/` texts
  are not redistributed; see `data/docs/SOURCES.md`)
- `figures/` all figures as SVG

## Reproducing

Python 3 standard library only, with `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, and
`GEMINI_API_KEY` in the environment; Google Chrome renders the figures and PDF.
Pipeline order, from `code/`: build_battery, run_battery, rate_sas, embed, score,
audit_constitutions, stats_tests, exploratory, wish_digest, then make_wheels,
figs_extra, make_kaf_map, build_paper. Full-study API cost was under 50 US dollars.

## Citation

Singh, B. (2026). Twelve Houses of a Digital Mind: Rock, Vapor, and Silence in AI
Self-Accounts. Apart Research Digital Minds Sprint.

The KAF framework repository predates this sprint and is private; available on request.

## License

Code under the MIT License; paper text, instrument, figures, and data under CC BY 4.0.
Model answers in `data/` are outputs of the named commercial models, provided for
research reproducibility.
