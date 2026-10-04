# ML-11 research-page design review

**Date:** 4 October 2026 · **Author:** Orbin Sunny · Prepared with AI assistance.

This review precedes the paper build. It separates sources about communicating research from the notebooks that supply this paper's empirical evidence. No source below supplies this project's model scores.

## Sources inspected and judgments

| Source | What I learned | Decision for this paper |
|---|---|---|
| [Scientific Reports: submission guidelines](https://www.nature.com/srep/author-instructions/submission-guidelines) | A concise abstract should stand alone and summarize results and implications; manuscript structure and figure legends make the argument inspectable. | Use a five-sentence abstract, a descriptive question title, and explicit methods, results and limitations. This is an internship research artifact, not a journal submission or peer-reviewed article. |
| [Distill: article authoring guide](https://distill.pub/guide/) | Author/date metadata, links to citations, a bounded reading column, wider figures and an appendix support web-native research. | Keep visible author/date metadata, a contents rail on desktop, and figures next to the claims they support. Plain HTML is sufficient for this artifact. |
| [Hohman et al.: Communicating with Interactive Articles](https://distill.pub/2020/communicating-with-interactive-articles/) | Interaction should serve a reader's task; maintenance, mobile usability and accessibility affect whether it is worthwhile. The live article illustrates a strong title/byline hierarchy and substantial captions. | Static charts and directly visible metric tables answer this paper's questions. Avoid hiding results behind a widget. Use anchors and optional technical details for navigation. |
| [Pineau: Machine Learning Reproducibility Checklist v2.0](https://www.cs.mcgill.ca/~jpineau/ReproducibilityChecklist-v2.0.pdf) | Dataset statistics, exclusions, split details, model settings, dependencies, commands and variation belong beside reported results. | Link the executed notebooks and aggregate receipts; state seed 42, model settings, metric definitions and unequal fold sizes. Do not manufacture confidence intervals or independent replications. |
| [Datawrapper: annotating visualizations](https://www.datawrapper.de/academy/annotate-tab) | A chart needs a clear message, population/context, notes, source attribution and an alternative description. | Put the denominator, split, units and lower-is-better direction on each error chart. Add captions with one takeaway and a receipt link. |
| [Datawrapper: customizing bar charts](https://www.datawrapper.de/academy/customizing-your-bar-chart) | Value labels and deliberate axis ranges help comparison; checking different screen sizes is part of chart design. | Use zero-based error bars, direct values and a consistent method palette; verify desktop and mobile emulation. |
| [W3C WAI: complex images](https://www.w3.org/WAI/tutorials/images/complex/) | A short alternative description identifies a figure; nearby text or a structured table can communicate its essential detail. | Every figure has meaningful alt text, a visible caption and adjacent numeric tables. Content must remain readable without scripts or color discrimination. |
| [GitHub: configuring a Pages source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) | Branch publication accepts the repository root or its root `/docs` directory; pushed source files trigger deployment. | The starter is nested, so publish a generated root `docs/` folder from `main`; retain source and build code in the starter's `work/`. Use relative assets and `.nojekyll`. |

## Formats considered

| Format | Advantage | Concern for this work |
|---|---|---|
| Notebook HTML export | Preserves code and outputs directly | Long audit outputs obscure the research question; notebook UI is poorly suited to skimming this paper |
| PDF as the only output | Familiar archival layout | Harder to read on a narrow screen, and makes notebook navigation less convenient |
| Plain HTML article + executed notebook | Readable on mobile; preserves inspectable evidence in the repository | Requires explicit checks that regenerated values, tables and figures agree |

**Choice:** plain HTML article with print styles, static figures, semantic tables, notebook links and a reproducible builder. Use restrained ink/teal/amber colors, a serif headline, short paragraphs and sufficient whitespace. No analytics, external fonts or runtime framework are needed.

## Evidence and chart plan

1. **Original client holdout:** show peer rule, shallow tree and forest on the same 760 supported pages; put validation selection next to test results. A tiny test difference is descriptive, not statistically established superiority.
2. **Split audit:** compare row-random versus client-grouped out-of-fold results on their common 11,911-page pool. Keep the pooled-CTR reference visible. This is a later audit of inspected clients, not a new untouched test.
3. **Review allocation:** compare canonical and capped top-20 client concentration; list all action archetype counts. The cap changes allocation, not measured editorial utility or fairness.

## Claims a skim reader must retain

- The main quantitative study uses the 30,000-page starter snapshot, not all 78,835,655 warehouse fact rows.
- A separate March warehouse development exercise checks window and availability rules; it is not the source of the main CTR-regression numbers.
- The peer rule wins the original validation comparison. The later grouped audit favors the naive pooled-CTR reference on exposure-weighted error.
- Independent editorial judgments, future generalization, edit effects and revenue are unavailable.
- Update age and recent decline are review context, not evidence that a refresh works.

## Review checklist before publication

- All nine assignment sections, including abstract and linked FlyRank data credit.
- Five complete abstract sentences; population and primary result agree with receipts.
- Tables and charts regenerated from the same receipts; split populations never mixed.
- Desktop and narrow-screen reading checked; no clipped content or missing assets.
- Public output contains aggregates only; no raw queues, private queries, client URLs or credentials.
- Exact live URL recorded on one line in `submission/paper_url.txt`.

Source review is a design judgment, not a claim of endorsement by the cited publishers.
