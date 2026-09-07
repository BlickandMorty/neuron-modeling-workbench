# Model card: teaching E/I circuit 0.1

This is an independently written educational adaptation of the [Brian2 Wang (2002) example](https://brian2.readthedocs.io/en/2.10.1/examples/frompapers.Wang_2002.html), credited to Klaus Wimmer and Marcel Stimberg. It is not a reproduction of Wang's decision experiment, Susin's AdEx network, or a human ketamine study. AI assisted implementation; learner mastery is not assumed.

## Equations and provenance

For each cell, capacitance times the voltage derivative equals the sum of electrical currents:

$$C\frac{dV}{dt}=-g_L(V-E_L)-I_A-I_N-I_G-I_{ext}+I_{pulse}.$$

The current convention is outward-positive: $I_A=g_A(V-E_E)$ and $I_G=g_G(V-E_I)$. Plots display their negatives so an inward/depolarizing current is positive. Voltage is clamped during the refractory interval; synaptic states continue evolving.

$$I_N=g_N(1-b)S\frac{V-E_E}{1+\exp(-0.062V_{mV})/3.57}.$$

Magnesium is fixed at the source's 1 mM reference. $b$ is a fractional reduction in effective conductance. It is constant throughout each run: there is no absorption, clearance, measured receptor occupancy or simulated infusion timeline.

Each excitatory cell carries a presynaptic gate:

$$\dot{x}=-x/(2\,ms),\qquad \dot{s}=-s/(100\,ms)+(0.5/ms)x(1-s).$$

A spike increments $x$ after 0.5 ms. $S$ is the sum of excitatory presynaptic gates, broadcast to each postsynaptic cell. This shortcut requires the homogeneous all-to-all architecture and shared delays used here. AMPA and GABA conductances decay exponentially and jump at incoming spikes.

| Quantity | E cells | I cells | Origin |
|---|---:|---:|---|
| Rest / threshold / reset | −70 / −50 / −55 mV | Same | Brian2 reference |
| Capacitance | 500 pF | 200 pF | Brian2 reference |
| Leak conductance | 25 nS | 20 nS | Brian2 reference |
| Refractory interval | 2 ms | 1 ms | Brian2 reference |
| Excitatory / inhibitory reversal | 0 / −70 mV | Same | Brian2 reference |
| AMPA / GABA decay | 2 / 5 ms | Same | Brian2 reference |
| NMDA rise / decay | 2 / 100 ms | Same | Brian2 reference |
| Recurrent AMPA incoming from E | 0.05 × 1600/NE nS | 0.04 × 1600/NE nS | Reference scaling |
| Recurrent NMDA incoming from E | 0.165 × 1600/NE nS | 0.13 × 1600/NE nS | Reference scaling |
| GABA incoming from I | 1.3 × 400/NI nS | 1.0 × 400/NI nS | Reference scaling |
| External event conductance | 2.1 nS | 1.62 nS | Brian2 reference |
| External input | 1000 independent sources/cell × 2.4 Hz | Same | Reference aggregate rate |
| Cell count | 80 | 20 | Laptop teaching choice |
| Test current, 800–900 ms | 150 pA | 0 pA | Teaching choice, not a threat cue |

## Departures and exploratory assumptions

All-to-all connections include autapses. There are no anatomical regions or selective decision pools. Reducing population size and scaling weights preserves a reference total coupling scale, **not** the original fluctuations, correlation structure, or behavior. Advanced controls offer 100, 250 and 500 cells at an 80:20 E:I ratio; `size_sensitivity.py` tests their mean-rate sensitivity. A comparison with the original 2,000-cell model and exact replication remain later tasks. See [the research path](RESEARCH_PATH.md) for the distinction between cell count and whole-brain coverage.

Default exposure fractions are bE=0.10 and bI=0.30, selected to illustrate differential effects, not extracted from a ketamine dose. Reference circuit scale factors equal 1. The default hypothesis changes inhibitory strength to 0.85. Alternative hypotheses change recurrent excitation (both AMPA and NMDA incoming from E) or external Poisson input frequency. Only one factor changes at a time. The factor has no validated mapping to PTSD or severity.

Euler integration uses dt=0.1 ms by default; verification repeats at 0.05 ms. Recording every 1 ms is distinct from integration resolution. Initial voltage is seeded uniform −70 to −60 mV; initial conductances/gates are zero. Identical random seeds make within-resolution condition comparisons paired. Different dt changes the random event discretization; convergence is assessed over seeds, not exact spike equality.

## Measurements

- Firing traces: spikes in 5-ms bins divided by population size and bin duration in seconds.
- Pre-input mean: the 300 ms before the pulse. Pulse mean: 800–900 ms by default. Post-input mean: pulse end + 200 ms through run end.
- Pulse-minus-pre is descriptive, **not** a causal stimulus effect. For a causal test, repeat with pulse=0 using matched seeds; do not confuse this with a no-drug control.
- PSD: Welch spectrum of 1-ms population spike-count rates after pulse end + 200 ms. Hann windows of 256 samples with 128 overlap; constant detrending; sample rate 1000 Hz. Resolution is approximately 3.91 Hz. Integrated 30–90 Hz power is a descriptive band statistic, not proof of a gamma oscillation. A short record or absent peak is a valid outcome.
- PSD units: Hz²/Hz (rate squared per frequency); integrated power: Hz². No LFP/EEG forward model exists.
- Synaptic plots: one example cell per population, not a population-average current.
- Matched differences: perturbed minus control for each seed, separately for reference and hypothesis circuits. Dots are seed results; bars are sample standard deviation. They are not patient intervals or full parameter uncertainty.

## Scope boundary

No BDNF, spine turnover, learning rule, pharmacokinetics, autonomic system, trauma memory, regional anatomy, consciousness or symptom scale is simulated. There is no baked-in therapeutic improvement and no calibrated PTSD diagnosis. The evidence library discusses these topics without pretending that a slider models them.

## Reproduction and integrity

`python circuit_lab.py --seeds 11 22 33` creates an immutable, uniquely named run directory. Use `--dt 0.05` for the resolution comparison. Raw arrays, configuration, model-source hash, environment versions, metrics and a learner interpretation template are retained. Failed runs retain a failed manifest. Loading verifies hashes of numerical outputs. `python verify_circuit.py` performs the documented numerical and negative-control checks without selecting favorable seeds.
