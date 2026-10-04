# ML-11 paper · ML-12 case-study update

**Author:** Orbin Sunny · **Lane:** CTR opportunity scoring · **Date:** 4 October 2026

[Read the published paper](https://orbin123.github.io/flyrank-ml-internship/) ·
[Open the executed capstone](../notebooks/capstone.ipynb) ·
[Research-page design review](../research_page_design.md)

The paper source is `index.template.html` and `styles.css`. The builder reads only committed aggregate receipts, verifies their hashes and frozen claims, and writes the publishable site to the **repository-root** `docs/` directory. This differs from the existing technical documentation in the nested starter's `docs/` folder. Figures also regenerate into `work/figures/`.

From the nested starter directory, with Python 3.11:

```bash
pip install -r work/requirements-w05.txt
python work/scripts/run_capstone.py
```

This runs the model comparison, validation audit and action playbook top to bottom, then executes the capstone and rebuilds the paper. For a receipt-only rebuild:

```bash
python work/scripts/build_paper.py
```

The static build requires no warehouse credentials. The separate March warehouse notebook is cited as saved development evidence; it needs approved gated access for a new run and is not silently folded into the main starter-snapshot study.

Publish `main` → root `/docs` with GitHub Pages. Assets use relative paths and `.nojekyll` disables Jekyll processing. The exact public URL is recorded on one line in `submission/paper_url.txt`. Local checks cover sections, links/assets, receipt agreement, missing labels, public-output restrictions and URL format; live deployment and portal submission are verified separately.

The main study reports a negative result: the peer rule beats the learned challengers on the original exposure-weighted objective, and a naive pooled-CTR reference wins the later grouped audit. It does not measure editorial actionability, future CTR, causal refresh effects or revenue.

For ML-12, the paper's abstract and introduction explicitly connect that result to FlyRank's limited-attention content-review problem. The executed capstone notebook closes with a timed five-minute demo outline, a copy-ready social post and a three-sentence employer summary.
