# Experiment 002: does circuit size change the conclusion?

**Question:** Are post-input firing rates insensitive to moving from 100 to 250 to 500 cells while retaining the reference total coupling scale?

**Prediction and method:** No direction was specified in advance for the larger runs. Fluctuations and state transitions could change even with inverse-population-size synaptic weights. Four conditions, 80:20 E:I ratio, seeds 11/22/33, dt=0.1 ms, duration 2 seconds, pulse 150 pA at 800–900 ms. The 100-cell baseline was already inspected and was reused after configuration/source/output-integrity checks. This is not a blinded preregistered experiment. The 250- and 500-cell runs were computed after recording the fixed size protocol; no favorable size was selected.

**Primary measure:** Per-neuron excitatory and inhibitory firing during the post-input window (1100–2000 ms). Descriptive flag: a mean shift from 100 cells greater than max(2 Hz, 25% of the 100-cell mean). This is not a statistical significance threshold or clinical tolerance.

## Observed result

Excitatory firing, mean ± sample SD across three seeds, Hz per neuron:

| Condition | 100 cells | 250 cells | 500 cells |
|---|---:|---:|---:|
| Reference / control | 1.292 ± 0.097 | 2.050 ± 0.327 | 2.361 ± 0.119 |
| Reference / NMDA reduction | 49.255 ± 1.571 | 59.700 ± 1.588 | 66.102 ± 0.958 |
| Hypothesis / control | 1.907 ± 0.079 | 3.696 ± 0.059 | 3.819 ± 0.376 |
| Hypothesis / NMDA reduction | 56.699 ± 1.335 | 65.722 ± 1.541 | 73.456 ± 0.479 |

Two of 16 size/condition/cell-type comparisons exceeded the descriptive threshold: 500-cell excitatory firing in both perturbed conditions. Reference perturbed E firing rose by 16.847 Hz relative to 100 cells; hypothesis perturbed E firing rose by 16.757 Hz. Other changes remain visible even when not flagged. The broad threshold must not turn them into proof of equality.

**Interpretation:** The observed mean rates are size-sensitive. The NMDA perturbation increased E firing at all three tested sizes under these selected assumptions, but its magnitude is not size-independent. These are model results, not ketamine effect sizes in people. This experiment does not establish why the rates changed: changing finite-size fluctuations is one plausible explanation, not a separately isolated causal finding.

**Falsifier outcome:** The strong claim that preserving total coupling preserves the measured rates is weakened. Keep the 100-cell example for learning with this limitation attached; do not present it as a numerically converged cortical model.

**Stopping rule:** The fixed three-size, three-seed grid is complete. No further parameter tuning or larger run was selected to erase this result.

**Next test:** For a replication milestone, recover the selected published architecture and initial conditions, then assess sizes, observation duration, initial states and step size separately. Additional seeds and durations would be needed to characterize state-transition probabilities reliably. Increasing size in this homogeneous circuit alone does not add anatomical validity.

## Artifacts and reproduction

- [Protocol, run links, source hashes and descriptive checks](../results/size_sensitivity/20260906T140909Z-07b518e4/size_report.json)
- [All 36 condition/seed/size metric rows](../results/size_sensitivity/20260906T140909Z-07b518e4/metrics.csv)
- [Summary table](../results/size_sensitivity/20260906T140909Z-07b518e4/summary.csv)
- [Size comparison figure](../results/size_sensitivity/20260906T140909Z-07b518e4/size_comparison.png)

Run `python size_sensitivity.py` inside the project environment. Matching complete, integrity-checked runs can be reused; reuse is explicitly logged. Twenty-four new circuit simulations were computed for this experiment; the 12 standard 100-cell runs were reused.

**Boundary:** Only three sizes, three seeds and one parameter setting. No empirical recordings, no new brain regions, no convergence of spectra or spike timing established, no human uncertainty intervals. No full drug model, trauma learning or treatment prediction. AI assisted implementation and this initial interpretation; the learner's own explanation is still an ownership exercise.
