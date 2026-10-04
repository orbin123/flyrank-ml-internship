# FlyRank ML Internship — Orbin Sunny

[Read the ML-11 research paper](https://orbin123.github.io/flyrank-ml-internship/) ·
[Executed capstone notebook](flyrank-ml-internship-starter-main/work/notebooks/capstone.ipynb) ·
[Deployed URL file](flyrank-ml-internship-starter-main/submission/paper_url.txt)

The starter repository is nested in [`flyrank-ml-internship-starter-main/`](flyrank-ml-internship-starter-main/). All analysis, paper source and reproducibility instructions live in its [`work/`](flyrank-ml-internship-starter-main/work/) directory. The root `docs/` folder contains only the generated public research page and aggregate evidence, published with GitHub Pages.

The paper compares CTR benchmarks on the approved 30,000-page starter snapshot. Learned models do not improve the original exposure-weighted holdout result; the later grouped audit also favors a naive reference. The proposed editorial queue still requires independent human-review evidence. The separate warehouse data-contract exercise is clearly distinguished from these main results.

## Reproduce

Use Python 3.11, create a virtual environment, then from the nested starter directory:

```bash
pip install -r work/requirements-w05.txt
python work/scripts/run_capstone.py
```

See the [paper build instructions](flyrank-ml-internship-starter-main/work/paper/README.md) and [research-page design review](flyrank-ml-internship-starter-main/work/research_page_design.md). No new datasets or row-level queues are committed. Built on the [FlyRank ML Internship dataset](https://flyrank.ai).
