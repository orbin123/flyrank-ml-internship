"""Build the public ML-11 paper from checked aggregate receipts, without raw data."""
from __future__ import annotations

import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

STARTER = Path(__file__).resolve().parents[2]
REPO = STARTER.parent
SITE = REPO / "docs"
PAPER = STARTER / "work/paper"
FIGURES = STARTER / "work/figures"
URL = "https://orbin123.github.io/flyrank-ml-internship/"
GITHUB = "https://github.com/orbin123/flyrank-ml-internship"
SOURCE = GITHUB + "/blob/main/flyrank-ml-internship-starter-main"
HASH = "c43bdac4eccfa17fcd8a33974fe36f2c998c03a3ae3af8d80cf712abab5d6396"
RECEIPTS = ["w05_model_metrics.json", "w06_validation_audit_metrics.json",
            "w07_action_playbook_metrics.json"]
REQUIRED_SECTIONS = ["abstract", "introduction", "data", "methodology", "results",
                     "limitations", "recommendations", "reproducibility", "acknowledgments"]


def load_evidence():
    evidence = {name: json.loads((STARTER / "work/outputs" / name).read_text())
                for name in RECEIPTS}
    model, audit, playbook = (evidence[name] for name in RECEIPTS)
    for receipt in evidence.values():
        assert receipt["data_sha256"] == HASH
        assert receipt["seed"] == 42
        assert receipt["independent_editorial_labels"] == 0
        assert receipt["editorial_precision_at_20"] is None
    for name, expected in playbook["source_receipts"].items():
        assert hashlib.sha256((STARTER / name).read_bytes()).hexdigest() == expected
    assert model["selected_on_validation"] == "Week-4 peer rule (train-only)"
    assert model["features"] == ["avg_position", "content_type", "days_since_last_update"]
    assert {r["pages"] for r in model["test_metrics"]} == {760}
    assert {r["clients"] for r in model["test_metrics"]} == {6}
    # Narrative/captions are reviewed for this frozen analysis. Changed evidence
    # must fail visibly instead of silently placing new numbers in old claims.
    np.testing.assert_allclose(
        [r["weighted_MAE_pp"] for r in model["test_metrics"]],
        [0.3834359486, 0.3880381144, 0.3855207364], rtol=0, atol=1e-9)
    np.testing.assert_allclose(
        [r["weighted_MAE_pp"] for r in model["validation_metrics"]],
        [0.227869727, 0.2601860993, 0.2573805723], rtol=0, atol=1e-9)
    np.testing.assert_allclose(
        [r["weighted_MAE_pp"] for r in audit["oof_comparison"]],
        [0.2366209858, 0.2335581422, 0.2208385675,
         0.2508988056, 0.2585305981, 0.2645573203], rtol=0, atol=1e-9)
    assert audit["common_oof_pages"] == 11911 and audit["common_oof_clients"] == 28
    assert all(r["overlap_clients"] == 0 for r in audit["grouped_fold_structure"])
    assert audit["leak_probes_removed"] is True
    assert (playbook["test_supported_pages"], playbook["test_deferred_pages"],
            playbook["positive_gap_candidates"], playbook["test_nonpositive_gap_pages"]) == (760, 61, 493, 267)
    assert [r["pages"] for r in playbook["archetype_summary"]] == [30, 423, 6, 33, 1]
    assert [r["largest_client_slot_share"] for r in playbook["allocation"]] == [0.95, 0.25]
    assert [r["clients"] for r in playbook["allocation"]] == [2, 6]
    assert playbook["human_reviews_completed"] == playbook["edits_performed"] == 0
    assert playbook["automated_edits_allowed"] is False
    assert playbook["refresh_effect"] is playbook["expected_recovered_clicks"] is None
    return evidence, model, audit, playbook


def table(caption, headers, rows):
    out = ['<div class="table-wrap" tabindex="0" role="region" aria-label="'
           + html.escape(caption, quote=True) + '"><table'
           + (' class="metric-table"' if len(headers) >= 4 else '') + '><caption>' + html.escape(caption)
           + '</caption><thead><tr>']
    out.extend('<th scope="col">' + html.escape(h) + '</th>' for h in headers)
    out.append('</tr></thead><tbody>')
    for row in rows:
        out.append('<tr><th scope="row">' + html.escape(str(row[0])) + '</th>')
        for value in row[1:]:
            numeric = isinstance(value, (int, float))
            rendered = f"{value:.6f}" if isinstance(value, float) else str(value)
            out.append('<td' + (' class="numeric"' if numeric else '') + '>'
                       + html.escape(rendered) + '</td>')
        out.append('</tr>')
    out.append('</tbody></table></div>')
    return ''.join(out)


def save_figure(fig, name):
    for destination in [SITE / "assets", FIGURES]:
        path = destination / name
        fig.savefig(path, format="svg", metadata={"Date": None},
                    facecolor="white")
        # Matplotlib leaves spaces at the ends of SVG path lines. Keep generated
        # assets reviewable and make git's whitespace checks useful for the repo.
        path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
    plt.close(fig)


def make_figures(model, audit, playbook):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13,
                         "svg.fonttype": "path", "svg.hashsalt": "flyrank-ml11",
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.spines.left": False, "axes.edgecolor": "#cad8d1",
                         "text.color": "#203433", "axes.labelcolor": "#203433",
                         "xtick.color": "#596b69", "ytick.color": "#203433"})
    fig, ax = plt.subplots(figsize=(9.6, 4.6))
    fig.subplots_adjust(left=.25, right=.95, top=.78, bottom=.20)
    values = [r["weighted_MAE_pp"] for r in model["test_metrics"]]
    bars = ax.barh(["Peer rule", "Shallow tree", "Random forest"], values,
                   color=["#176e64", "#788780", "#b87930"], height=.52)
    ax.invert_yaxis()
    ax.set_xlim(0, .46)
    ax.set_xlabel("Impression-weighted CTR MAE (pp) · lower is better", fontsize=12, labelpad=16)
    ax.set_xticks([0, .1, .2, .3, .4])
    ax.grid(axis="x", color="#e4ece7", linewidth=.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0, pad=12)
    ax.bar_label(bars, labels=[f"{x:.6f}" for x in values], padding=7, fontsize=12)
    fig.text(.065, .92, "The peer rule narrowly leads on the held-out clients", fontsize=17, weight="bold")
    fig.text(.065, .85, "760 supported pages · 6 clients · identical evaluation pool", fontsize=12, color="#596b69")
    save_figure(fig, "holdout.svg")

    fig, ax = plt.subplots(figsize=(9.6, 5.2))
    fig.subplots_adjust(left=.12, right=.96, top=.73, bottom=.25)
    rows = audit["oof_comparison"]
    x = np.arange(3)
    ax.bar(x - .17, [r["weighted_MAE_pp"] for r in rows[:3]], width=.32,
           color="#b9cbc0", label="Row-random folds")
    grouped = ax.bar(x + .17, [r["weighted_MAE_pp"] for r in rows[3:]], width=.32,
                     color="#176e64", label="Client-grouped folds")
    # Direct labels carry values independent of color or hover interaction.
    for i, row in enumerate(rows[:3]):
        ax.text(i-.17, row["weighted_MAE_pp"]+.007, f'{row["weighted_MAE_pp"]:.6f}',
                ha="center", fontsize=11)
    ax.bar_label(grouped, labels=[f'{r["weighted_MAE_pp"]:.6f}' for r in rows[3:]],
                 padding=6, fontsize=11)
    ax.set_xticks(x, ["Pooled training CTR", "Peer rule", "Random forest"])
    ax.set_ylim(0, .32)
    ax.set_ylabel("Weighted CTR MAE (pp)", fontsize=12)
    ax.grid(axis="y", color="#e4ece7", linewidth=.8)
    ax.set_axisbelow(True)
    ax.legend(loc="upper center", bbox_to_anchor=(.5, -.2), ncol=2, frameon=False, fontsize=12)
    fig.text(.065, .93, "The ranking changes when entire clients are held out", fontsize=17, weight="bold")
    fig.text(.065, .865, "11,911 common supported pages · 28 clients · lower is better", fontsize=12, color="#596b69")
    fig.text(.065, .80, "Five-fold diagnostic audit; not a new untouched test", fontsize=11, color="#596b69")
    save_figure(fig, "split-audit.svg")

    fig, ax = plt.subplots(figsize=(9.6, 4.4))
    fig.subplots_adjust(left=.30, right=.95, top=.75, bottom=.21)
    values = [100 * r["largest_client_slot_share"] for r in playbook["allocation"]]
    bars = ax.barh(["Canonical top-20\n2 clients", "Capped batch\n6 clients"], values,
                   color=["#b87930", "#176e64"], height=.48)
    ax.invert_yaxis()
    ax.set_xlim(0, 115)
    ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_xlabel("Largest client's share of the 20 review slots", fontsize=12, labelpad=14)
    ax.grid(axis="x", color="#e4ece7", linewidth=.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0, pad=12)
    ax.bar_label(bars, labels=["19 / 20", "5 / 20"], padding=7, fontsize=12)
    fig.text(.065, .92, "A client cap spreads review attention", fontsize=17, weight="bold")
    fig.text(.065, .845, "Same 20-slot capacity · at most 5/client in the capped batch", fontsize=12, color="#596b69")
    save_figure(fig, "allocation.svg")

    # Phone figures retain readable type and shorter direct value labels.
    # Exact six-decimal values remain in the adjacent semantic HTML tables.
    fig, ax = plt.subplots(figsize=(5, 4.2))
    fig.subplots_adjust(left=.28, right=.95, top=.74, bottom=.23)
    values = [r["weighted_MAE_pp"] for r in model["test_metrics"]]
    bars = ax.barh(["Peer rule", "Shallow\ntree", "Random\nforest"], values,
                   color=["#176e64", "#788780", "#b87930"], height=.5)
    ax.invert_yaxis()
    ax.set_xlim(0, .52)
    ax.set_xticks([0, .2, .4])
    ax.set_xlabel("Weighted CTR MAE (pp)\nLower is better", fontsize=12, labelpad=12)
    ax.grid(axis="x", color="#e4ece7")
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0, pad=8, labelsize=12)
    ax.bar_label(bars, labels=[f"{v:.3f}" for v in values], padding=5, fontsize=12)
    fig.text(.065, .91, "The peer rule narrowly leads", fontsize=15, weight="bold")
    fig.text(.065, .83, "Same 760 pages · 6 held-out clients", fontsize=11, color="#596b69")
    save_figure(fig, "holdout-mobile.svg")

    fig, ax = plt.subplots(figsize=(5, 5.2))
    fig.subplots_adjust(left=.16, right=.97, top=.67, bottom=.24)
    x = np.arange(3)
    for offset, group, color in [(-.17, rows[:3], "#b9cbc0"), (.17, rows[3:], "#176e64")]:
        bars = ax.bar(x+offset, [r["weighted_MAE_pp"] for r in group], width=.32, color=color,
                      label="Row-random" if offset < 0 else "Client-grouped")
        ax.bar_label(bars, labels=[f'{r["weighted_MAE_pp"]:.3f}' for r in group], padding=5, fontsize=10)
    ax.set_xticks(x, ["Pooled\nCTR", "Peer\nrule", "Random\nforest"], fontsize=11)
    ax.set_ylim(0, .32)
    ax.set_ylabel("Weighted CTR MAE (pp)", fontsize=11)
    ax.tick_params(axis="y", labelsize=10)
    ax.grid(axis="y", color="#e4ece7")
    ax.set_axisbelow(True)
    ax.legend(loc="upper center", bbox_to_anchor=(.45, -.25), ncol=2, frameon=False, fontsize=10)
    fig.text(.065, .92, "Client holdout changes\nthe ranking", fontsize=15, weight="bold")
    fig.text(.065, .79, "11,911 pages · 28 clients · lower is better", fontsize=10, color="#596b69")
    fig.text(.065, .735, "Five-fold diagnostic, not a new test", fontsize=10, color="#596b69")
    save_figure(fig, "split-audit-mobile.svg")

    fig, ax = plt.subplots(figsize=(5, 3.8))
    fig.subplots_adjust(left=.30, right=.94, top=.68, bottom=.24)
    values = [100*r["largest_client_slot_share"] for r in playbook["allocation"]]
    bars = ax.barh(["Canonical\n2 clients", "Capped\n6 clients"], values,
                   color=["#b87930", "#176e64"], height=.48)
    ax.invert_yaxis()
    ax.set_xlim(0, 127)
    ax.set_xticks([0, 50, 100], ["0%", "50%", "100%"])
    ax.set_xlabel("Largest client's share\nof 20 review slots", fontsize=12, labelpad=12)
    ax.tick_params(axis="y", length=0, pad=8, labelsize=12)
    ax.grid(axis="x", color="#e4ece7")
    ax.set_axisbelow(True)
    ax.bar_label(bars, labels=["19/20", "5/20"], padding=5, fontsize=12)
    fig.text(.065, .92, "Spread review attention", fontsize=15, weight="bold")
    fig.text(.065, .82, "Proposed cap: 5 slots per client", fontsize=11, color="#596b69")
    save_figure(fig, "allocation-mobile.svg")


class PageAudit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sections, self.links, self.images, self.ids = [], [], [], []
        self.h1 = 0
    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "section":
            self.sections.append(attrs.get("id"))
        if tag == "h1":
            self.h1 += 1
        if tag == "a":
            self.links.append(attrs["href"])
        if tag == "img":
            assert attrs.get("alt"), "Every research figure needs alternative text"
            self.images.append(attrs["src"])
        if tag == "source":
            self.images.append(attrs["srcset"])
        assert tag not in {"script", "iframe"}, "Public paper has no runtime or embedded third-party data"


def verify_site():
    content = (SITE / "index.html").read_text()
    parser = PageAudit()
    parser.feed(content)
    assert parser.sections == REQUIRED_SECTIONS and parser.h1 == 1
    assert len(set(parser.ids)) == len(parser.ids)
    assert len(parser.images) == 6
    assert "@@" not in content
    assert '<a href="https://flyrank.ai">Built on the FlyRank ML Internship dataset</a>' in content
    allowed_hosts = {"github.com", "flyrank.ai", "huggingface.co", "www.nature.com",
                     "distill.pub", "www.cs.mcgill.ca", "www.datawrapper.de", "www.w3.org"}
    for link in parser.links + parser.images + ["styles.css"]:
        if link.startswith("#"):
            assert link[1:] in parser.ids
        elif urlsplit(link).scheme:
            assert urlsplit(link).scheme == "https"
            assert urlsplit(link).hostname in allowed_hosts
        else:
            assert not Path(link).is_absolute()
            assert (SITE / link).resolve().is_relative_to(SITE.resolve())
            assert (SITE / link).is_file(), link
    # Do not publish datasets or row-level identifiers, even when pseudonymized.
    forbidden = re.compile(r"\b(?:hf_[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|"
                           r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})\b", re.I)
    for path in SITE.rglob("*"):
        if path.is_file():
            assert path.suffix not in {".csv", ".parquet", ".zip", ".feather"}
            assert not forbidden.search(path.read_text()), "Sensitive content found (not printed)"
    evidence = json.loads((SITE / "assets/evidence.json").read_text())
    def safe_keys(obj):
        if isinstance(obj, dict):
            assert not set(obj) & {"client_id", "content_id", "client_name", "url", "query", "token", "email"}
            for value in obj.values(): safe_keys(value)
        elif isinstance(obj, list):
            for value in obj: safe_keys(value)
    safe_keys(evidence)
    assert (STARTER / "submission/paper_url.txt").read_text() == URL + "\n"
    return {"required_sections": len(parser.sections), "figures": len(parser.images) // 2,
            "mobile_figure_variants": len(parser.images) // 2,
            "local_assets_and_anchors": "pass", "aggregate_only_evidence": "pass",
            "paper_url_format": "pass", "sensitive_content_scan": "pass"}


def build():
    evidence, model, audit, playbook = load_evidence()
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    make_figures(model, audit, playbook)
    abstract = (
        "This study asks whether a learned CTR benchmark improves the measurable surrogate for an editorial review queue over a transparent peer rule. "
        "It uses a 30,000-page anonymized starter snapshot, retaining 12,009 pages across 28 clients under an explicit exposure and position policy. "
        "A shallow tree and random forest estimate same-window observed CTR using three allowlisted features, with training-only peers and disjoint client validation. "
        "The peer rule wins validation and records test weighted MAE of 0.383436 percentage points versus 0.385521 for the forest, while a later grouped audit favors a naive pooled-CTR reference. "
        "The resulting queue is proposed decision support for human inspection; independent editorial usefulness, future performance and causal edit benefits remain unmeasured."
    )
    assert len(re.split(r"(?<=[.!?])\s+(?=[A-Z])", abstract)) == 5
    validation = {r["method"]: r for r in model["validation_metrics"]}
    short = {"Week-4 peer rule (train-only)": "Peer rule", "shallow tree": "Shallow tree",
             "random forest": "Random forest", "naive training pooled CTR": "Pooled training CTR",
             "training-only peer rule": "Peer rule", "frozen Week-5 forest": "Random forest"}
    actions = {r["archetype"]: r for r in playbook["archetype_summary"]}
    action_order = [
        ("recent_update_observe", "Recently updated → observe"),
        ("stale_and_observed_decline", "Stale + observed decline → investigate"),
        ("top_visibility_low_capture", "Position 1–3 → snippet/intent review"),
        ("page_one_low_capture", "Position >3–10 → matched intent review"),
        ("striking_distance_low_capture", "Position >10–20 → coverage/linking review")]
    context = {
        "REPO": GITHUB, "SOURCE": SOURCE, "DATA_HASH": HASH, "ABSTRACT": abstract,
        "DATA_TABLE": table("Two distinct analysis populations; results are not pooled",
            ["Analysis", "Source / window", "Scope"], [
                ["Main CTR study", "Bundled trailing-90-day starter snapshot; dates unspecified", "30,000 pages / 32 clients"],
                ["Warehouse development exercise", "v20260703 / March 2026 daily fact + client dimension", "9,841,378 source rows; 137 labeled pages / 5 clients"]]),
        "SPLIT_TABLE": table("Original seed-42 split; support thresholds are training-only",
            ["Partition", "Pages", "Clients", "Supported evaluation", "Deferred"],
            [[r["partition"].title(), r["pages"], r["clients"],
              int(r["evaluation_pages"]) if r["evaluation_pages"] is not None else "—",
              int(r["deferred_pages"]) if r["deferred_pages"] is not None else "—"] for r in model["split"]]),
        "HOLDOUT_TABLE": table("Original comparison: validation n=4,626; test n=760; all errors in pp",
            ["Method", "Validation weighted MAE", "Test weighted MAE", "Test page MAE", "Test equal-client MAE"],
            [[short[r["method"]], validation[r["method"]]["weighted_MAE_pp"],
              r["weighted_MAE_pp"], r["page_MAE_pp"], r["equal_client_MAE_pp"]] for r in model["test_metrics"]]),
        "AUDIT_TABLE": table("Audit common pool: n=11,911 / 28 clients; all errors in pp",
            ["Method / protocol", "Weighted MAE", "Page MAE", "Equal-client MAE"],
            [[short[r["method"]] + (" / grouped" if r["protocol"].startswith("grouped") else " / row-random"),
              r["weighted_MAE_pp"], r["page_MAE_pp"], r["equal_client_MAE_pp"]] for r in audit["oof_comparison"]]),
        "ACTION_TABLE": table("Proposed action branches in precedence order; 493 positive-gap test candidates",
            ["Branch / first action", "Pages", "Clients represented"],
            [[label, actions[key]["pages"], actions[key]["clients"]] for key, label in action_order])
    }
    page = (PAPER / "index.template.html").read_text()
    for key, value in context.items():
        page = page.replace("@@" + key + "@@", value)
    (SITE / "index.html").write_text(page)
    (SITE / ".nojekyll").write_text("")
    shutil.copyfile(PAPER / "styles.css", SITE / "styles.css")
    (SITE / "assets/evidence.json").write_text(json.dumps(evidence, indent=2, allow_nan=False) + "\n")
    (STARTER / "submission/paper_url.txt").write_text(URL + "\n")
    checks = verify_site()
    receipt = {"assignment": "ML-11", "paper_url": URL, "input_sha256": HASH,
               "source_receipt_sha256": {name: hashlib.sha256((STARTER / "work/outputs" / name).read_bytes()).hexdigest()
                                         for name in RECEIPTS},
               "published_file_sha256": {str(p.relative_to(SITE)): hashlib.sha256(p.read_bytes()).hexdigest()
                                         for p in sorted(SITE.rglob("*")) if p.is_file()},
               "checks": checks, "scope": "static build checks; deployment and portal submission verified externally"}
    (STARTER / "work/outputs/w08_paper_build_metrics.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("PASS: built paper, three figures and aggregate evidence; nine sections and public-output checks passed.")
    return receipt


if __name__ == "__main__":
    build()
