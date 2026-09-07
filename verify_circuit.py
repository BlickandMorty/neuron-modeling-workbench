"""Fixed validation protocol. Preserve results even when thresholds are not met."""
from dataclasses import replace
from pathlib import Path
import json
import numpy as np
from circuit_lab import Config, ROOT, conditions, run_comparison, simulate
from notebook_ui import save_static_summary


def main():
    base = Config(block_e=.1, block_i=.3)
    fine, examples, folder = run_comparison(replace(base, dt_ms=.05), progress=lambda s: print(s, flush=True),
                                            prediction="Resolution check: mean post-input rates should remain within max(2 Hz, 25%) of dt=0.1 ms.")
    save_static_summary(fine, examples, folder)
    from circuit_lab import load_run
    candidates = sorted((ROOT/"results"/"circuit").glob("*/manifest.json"), reverse=True)
    coarse = None
    for path in candidates:
        manifest = json.loads(path.read_text())
        if (manifest.get("status") == "complete" and manifest["seeds"] == [11,22,33]
                and manifest["variant"] == "inhibition" and manifest["variant_scale"] == .85
                and manifest["configurations"]["reference_perturbed"] == {**base.__dict__}):
            coarse, coarse_examples, coarse_folder = load_run(path.parent)
            break
    if coarse is None:
        coarse, coarse_examples, coarse_folder = run_comparison(base, progress=print,
                                                               prediction="Fixed coarse-resolution comparator; no tuning.")
    save_static_summary(coarse, coarse_examples, coarse_folder)
    checks = []
    for condition in coarse.condition.unique():
        for cell in ["e", "i"]:
            metric = cell+"_post_hz"
            a = float(coarse[coarse.condition == condition][metric].mean())
            z = float(fine[fine.condition == condition][metric].mean())
            tolerance = max(2., .25*abs(a))
            checks.append({"condition": condition, "metric": metric, "coarse_mean": a, "fine_mean": z,
                           "difference": z-a, "tolerance": tolerance, "within_tolerance": bool(abs(z-a) <= tolerance)})
    # A genuine numerical null control: identical configurations must reproduce identical outputs.
    quiet_base = replace(base, duration_ms=300, stimulus_on_ms=100, stimulus_off_ms=150, block_e=0., block_i=0.)
    null_cases = conditions(quiet_base, variant_scale=1.)
    arrays = [simulate(c) for c in null_cases.values()]
    null_exact = all(all(np.array_equal(arrays[0][key], other[key]) for key in arrays[0]
                         if isinstance(arrays[0][key], np.ndarray)) for other in arrays[1:])
    # Causal input control, with all other assumptions fixed; no expected direction asserted.
    no_pulse, no_examples, no_folder = run_comparison(replace(base, stimulus_pa=0.), seeds=(11,22,33),
                                                     prediction="Without the test pulse, state persistence may differ; either result is retained.", progress=print)
    save_static_summary(no_pulse, no_examples, no_folder)
    report = {"protocol": "post-input mean rate comparison across 3 seeds; threshold max(2 Hz, 25% coarse mean)",
              "coarse_run": str(coarse_folder), "fine_run": str(folder), "no_input_run": str(no_folder),
              "resolution_checks": checks, "all_rate_checks_pass": all(c["within_tolerance"] for c in checks),
              "zero_perturbation_identity_exact": null_exact,
              "limits": "Not convergence of spike timing, spectra, phase transitions, network size or clinical behavior. Different dt has different random draws."}
    target = folder/"verification.json"
    target.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(target)
    if not null_exact:
        raise AssertionError("Zero-control identity failed; do not interpret experiments")
    if not report["all_rate_checks_pass"]:
        print("WARNING: resolution sensitivity remains. Preserve it; do not claim converged results.")


if __name__ == "__main__":
    main()
