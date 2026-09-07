# Learn by looking, predicting, and calculating

Start with **Experiment** and inspect the saved example before running anything. It is simulated activity from 100 cells—not a picture of someone's brain. Four conditions let you separate a circuit assumption from an NMDA perturbation.

## Your first ten minutes

1. Open **Population firing**. Read the horizontal axis (milliseconds) and vertical axis (spikes per second per neuron). Find the brief input around 800–900 ms. A larger response is not automatically better function.
2. Open **Spike raster**. Each dot is one simulated spike; the row identifies a neuron. Compare dispersed activity with clustered firing.
3. Open **Synaptic currents**. Positive plotted current is inward; negative is outward. These traces belong to one example cell, not the whole population.
4. Open **Power spectrum**. A peak means a frequency contributes to fluctuations of the chosen signal. A noisy or flat-looking spectrum is not failure. It is not EEG.
5. Open **Matched differences**. Zero means no change on that metric. Each dot is a paired seed result. Ask whether the apparent effect is consistent across seeds.

Do not try to explain every plot at once. Pick one metric, state a prediction, run a comparison, and explain what could contradict you.

Wondering why this starts with 100 cells, or how scientists model whole brains? Read `research/RESEARCH_PATH.md` (linked at the bottom of the Learn tab). Advanced controls also let you test 250 and 500 cells; this changes circuit size, not anatomical coverage. The model equations and the measurements they predict matter more than a large neuron count by itself.

<details><summary><b>1 · Units: why a neuron changes voltage</b></summary>

Capacitance links current to the rate of voltage change: C dV/dt = current. With 500 pF capacitance and a 150 pA current, current/capacitance = 0.3 mV/ms before other currents are included. Check the units yourself: pA/pF = V/s = mV/ms.

Exercise: calculate the initial contribution of a 75 pA input. Then explain why doubling current does not necessarily double the eventual firing rate.

</details>

<details><summary><b>2 · Derivatives and time constants</b></summary>

A derivative is an instantaneous slope. The passive membrane obeys dV/dt = −(V−E_L)/tau, with tau=C/g_L. In E cells, 500 pF / 25 nS = 20 ms; in I cells, 200 pF / 20 nS = 10 ms.

After one time constant, a passive displacement retains exp(−1), approximately 37%, of its initial value. This passive result is not the complete spiking-network behavior.

Exercise: solve the passive equation and verify it by differentiating your answer. This is a small proof, not just a formula to memorize. Revisit the original single-neuron notebook for an analytic firing-rate comparison.

</details>

<details><summary><b>3 · Synapses, coupled equations, and signs</b></summary>

A synapse changes a conductance. Current also depends on voltage minus a reversal potential. At V=−60 mV, an excitatory reversal at 0 mV produces negative outward current—therefore positive inward current in our plots.

NMDA has a slow gate and a voltage-dependent magnesium factor. You can reduce its effective conductance independently on excitatory and inhibitory cells. Reducing excitation of an inhibitory cell can reduce inhibition elsewhere: the network consequence need not have the same sign as the receptor-level change.

Exercise: explain the difference between “NMDA current is smaller” and “population firing is smaller.” Predict both before checking.

</details>

<details><summary><b>4 · Feedback and stability</b></summary>

Recurrent excitation is positive feedback; inhibitory cells provide negative feedback. Delays and time constants change how the feedback unfolds. Linear algebra becomes useful when you collect state variables into a vector and study small perturbations with a Jacobian matrix.

Exercise: draw E→E, E→I, I→E and I→I connections. Mark signs. Later, derive a two-variable rate-model Jacobian and inspect eigenvalues. Do not directly apply that linear result to the entire nonlinear spiking model without checking its assumptions.

</details>

<details><summary><b>5 · Probability, controls, and uncertainty</b></summary>

External input is stochastic. A seed makes a run repeatable; it does not make it biologically true. Pair identical seeds across conditions to reduce irrelevant variation. Repeat seeds to see whether your inference depends on one noise realization.

The hypothesis and reference circuits are identical when the scale is 1. Reductions of zero should leave the control unchanged. These are negative controls. They must pass before interpreting more interesting differences.

Exercise: run scale=1, then bE=bI=0. Explain what must match and why. A real failure here would be a software or experiment-design problem, not a neuroscience discovery.

</details>

<details><summary><b>6 · Spectra and honest interpretation</b></summary>

A power spectrum decomposes signal variance by frequency. Window length sets frequency resolution. Detrending removes a mean or trend; it does not remove all confounds. More 30–90 Hz power can reflect broad fluctuations rather than a narrow gamma rhythm.

Exercise: compare a synthetic sine wave with random noise using scipy.signal.welch. Explain why changing bin width or observation length changes the plot. Then return to the circuit spectrum and name one conclusion it cannot support.

</details>

## Three experiments you can own

- **Target specificity:** hold the circuit fixed and contrast reduction on E cells with reduction on I cells. Measure post-input firing; allow either sign.
- **Hypothesis sensitivity:** choose one circuit factor and compare 0.85, 1.0 and 1.15. Keep input, seeds and resolution fixed. These values are illustrative, not PTSD measurements.
- **Input dependence:** compare pulse=150 pA with pulse=0. A pulse-minus-pre contrast alone cannot distinguish stimulus effects from spontaneous time variation.

## From an idea to a test

“Ketamine breaks automatic patterns” is not yet a measured variable. A later learning model could ask whether a previously learned response persists, generalizes, returns after a delay, or changes after safe experience. It would need an actual learning rule, a task, controls, and comparison with data. The present circuit does not learn or store a trauma memory.

Keep each result as: question → prediction → method → observed result → alternative explanation → boundary. A well-explained null result demonstrates scientific skill. AI-generated code is a starting aid; your derivations, corrections and defensible interpretations make the project yours.
