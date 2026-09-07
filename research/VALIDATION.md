# Release checks — 2026-09-06

## Executed checks

- `python -m unittest -q test_circuit_lab`: **22 tests passed**. Covers finite/invalid inputs, units, single-factor conditions, deterministic repeats, no-drive silence, targeted and full NMDA removal, synaptic decay, spike-count normalization, frequency-axis sanity, short-spectrum unavailability, saved-output integrity, failed manifests, evidence schema/cohort labels, notebook validity, plot-array correspondence, prediction requirements, UI parameter wiring including population size, evidence filtering, and size-summary calculations.
- `python -m nbconvert --to notebook --execute 02_ketamine_circuit.ipynb --output 02_ketamine_circuit.executed.ipynb --ExecutePreprocessor.timeout=120`: **completed** with no cell errors after the final size-control addition. Executed widgets are an archived snapshot; launch the original notebook and Run All to connect live controls.
- Package consistency check: **116 packages compatible**. Required widgets are installed in the existing project environment. No GPU or C++ compiler is required for this implementation.
- Fixed-seed numerical comparison: **8/8 post-input population mean-rate checks** met the prespecified max(2 Hz, 25%) tolerance when dt changed from 0.1 to 0.05 ms. Maximum absolute difference across these means: 0.3334 Hz rounded upward. This is not convergence of all observables.
- Zero-perturbation/identity configuration control: exact recorded-array agreement in the explicit four-condition check.
- No-pulse control: high activity remained possible, weakening the claim that the brief input was necessary for the observed high-activity regime. See Experiment 001.
- Size sensitivity: **2/16 descriptive checks flagged**, not hidden. Both 500-cell perturbed E-population means shifted substantially relative to 100 cells. See Experiment 002. Size independence is not established.

There are 60 saved circuit simulations across the standard, smaller-step, no-pulse, 250-cell and 500-cell sets (12 each), plus short test/control simulations. The size summary contains 36 rows by reusing the 12 standard runs alongside 24 larger runs; it does not claim 36 additional runs.

## Interface and artifact checks

The original notebook's connected widgets and matched-difference view were exercised in the browser before the size-control extension. The final extension is covered by callback tests and notebook execution. A final live-browser recheck was unavailable because the browser-control surface returned unavailable; it is not reported as completed.

Static circuit overviews and the size-comparison figure were visually inspected. Plots carry units and simulation labels. Tests check displayed numerical traces against the calculation functions. Source configurations and output hashes are saved; loading checks numerical-output integrity.

At the time of this September 6 validation, the original `neuron_lab.py` and `01_neuron_and_sql.ipynb` had no tracked diff, existing unrelated material was preserved, and no commit, push, public posting, resume change, or protection-setting change was made. Later publication does not change what happened during that checkpoint.

## Remaining limitations

The circuit is a teaching adaptation, not an exact published replication or empirically calibrated model. Evidence coverage is scoped, with abstract-only/inaccessible sources and remaining gaps marked. The model lacks regional anatomy, a measurement forward model, drug PK/PD, learning, autonomic feedback and slow plasticity.

Numerical warnings from upstream Brian2/pyparsing and the Windows Jupyter event-loop fallback did not fail execution. Jupyter is configured on local loopback; it is not a public or secured remote service. Do not expose the kernel or notebook server to other machines as part of this workflow.

AI assisted the code and reports. Tests establish defined software behavior; they do not establish independent learner mastery or biological truth.
