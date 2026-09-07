"""Fixed 100/250/500-cell experiment; size sensitivity is not biological validation."""
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import uuid

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import circuit_lab
from circuit_lab import Config, ROOT, load_run, run_comparison

SIZES = (100, 250, 500)
SEEDS = (11, 22, 33)


def size_config(total):
    if total not in SIZES:
        raise ValueError("This fixed protocol supports 100, 250, or 500 cells")
    return Config(n_e=total*4//5, n_i=total//5, block_e=.1, block_i=.3)


def summarize(table):
    rows = []
    for (size, condition), group in table.groupby(["cells", "condition"]):
        for cell in ("e", "i"):
            values = group[f"{cell}_post_hz"]
            rows.append(dict(cells=int(size), condition=condition, cell=cell,
                             mean_hz=float(values.mean()), sd_hz=float(values.std(ddof=1)),
                             seeds=len(values)))
    return pd.DataFrame(rows)


def main():
    folder = ROOT/"results"/"size_sensitivity"/(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"-"+uuid.uuid4().hex[:8])
    folder.mkdir(parents=True, exist_ok=False)
    source_hash = hashlib.sha256(Path(circuit_lab.__file__).read_bytes()).hexdigest()
    report = dict(status="running", question="Does post-input firing depend materially on circuit size?",
                  prediction="Changing size can change fluctuations and attractor entry despite constant total coupling; direction unspecified.",
                  protocol="100, 250, 500 cells; 80:20 E:I; four conditions; seeds 11,22,33; dt 0.1 ms; no parameter tuning.",
                  stopping_rule="Finish this fixed grid once. Preserve any size-dependent shifts; do not select a favorable size.",
                  source_sha256=source_hash,
                  experiment_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  model_version=circuit_lab.MODEL_VERSION, runs={},
                  baseline_status="100-cell results already inspected before this size protocol; not a blinded/preregistered baseline.",
                  boundary="Same homogeneous local circuit, not additional brain regions. Same seed numbers across sizes do not mean identical inputs. No patient inference.")
    target = folder/"size_report.json"
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    tables = []
    try:
        for total in SIZES:
            config = size_config(total)
            bundle = None
            for manifest_path in sorted((ROOT/"results"/"circuit").glob("*/manifest.json")):
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                if (manifest.get("status") == "complete" and manifest.get("source_sha256") == source_hash
                    and manifest["configurations"]["reference_perturbed"] == asdict(config)
                    and manifest["variant"] == "inhibition" and manifest["variant_scale"] == .85
                    and manifest["seeds"] == list(SEEDS)):
                    bundle = load_run(manifest_path.parent)
                    break
            reused = bundle is not None
            if bundle is None:
                bundle = run_comparison(config, seeds=SEEDS,
                    prediction=report["prediction"], progress=lambda text: print(f"{total} cells: {text}", flush=True))
            table, _, run_folder = bundle
            report["runs"][str(total)] = {"path": str(run_folder.relative_to(ROOT)), "reused": reused}
            table = table.copy()
            table["cells"] = total
            tables.append(table)
            target.write_text(json.dumps(report, indent=2), encoding="utf-8")
        combined = pd.concat(tables, ignore_index=True)
        summary = summarize(combined)
        combined.to_csv(folder/"metrics.csv", index=False)
        summary.to_csv(folder/"summary.csv", index=False)
        comparisons = []
        for _, row in summary[summary.cells != 100].iterrows():
            baseline = summary[(summary.cells == 100) & (summary.condition == row.condition) & (summary.cell == row.cell)].iloc[0]
            threshold = max(2., .25*abs(baseline.mean_hz))
            comparisons.append(dict(cells=int(row.cells), condition=row.condition, cell=row.cell,
                difference_hz=float(row.mean_hz-baseline.mean_hz), descriptive_threshold_hz=threshold,
                flagged=bool(abs(row.mean_hz-baseline.mean_hz)>threshold)))
        report["comparisons_to_100"] = comparisons
        report["flag_rule"] = "abs(mean difference) > max(2 Hz, 25% of 100-cell mean); chosen before larger runs. Descriptive flag, not a significance test or convergence certificate."
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True, layout="constrained")
        for ax, cell in zip(axes, ("e", "i")):
            for condition, group in summary[summary.cell == cell].groupby("condition"):
                ax.errorbar(group.cells, group.mean_hz, yerr=group.sd_hz, marker="o", capsize=4,
                            label=condition.replace("_", " "))
            ax.set(title=f"{'Excitatory' if cell == 'e' else 'Inhibitory'} population", xlabel="Total modeled cells",
                   ylabel="Post-input firing per neuron (Hz)", xticks=SIZES)
        axes[1].legend(fontsize=8)
        fig.suptitle("Size sensitivity • mean ± seed SD • not human uncertainty")
        fig.savefig(folder/"size_comparison.png", dpi=140)
        plt.close(fig)
        report["status"] = "complete"
        report["flagged_comparisons"] = sum(item["flagged"] for item in comparisons)
        report["artifacts_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in folder.iterdir() if p.suffix in (".csv", ".png")}
        print(summary.to_string(index=False), flush=True)
        print(f"Descriptive flags: {report['flagged_comparisons']}/{len(comparisons)}", flush=True)
    except Exception as error:
        report["status"] = "failed"
        report["error"] = repr(error)
        raise
    finally:
        target.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(target, flush=True)


if __name__ == "__main__":
    main()
