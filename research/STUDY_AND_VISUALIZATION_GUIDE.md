# Study, reproduction, and visual reasoning guide

Updated September 7, 2026. This is the entry point for learning every local
experiment and then replacing the teaching assumptions with models I can
explain. The existing lessons and results are preserved. This guide adds a map
through them; it does not replace their evidence or turn them into validated
biological findings.

## The central idea

A simulation is a sequence of translations:

`question -> assumptions -> equations -> parameters -> arrays -> checks -> figure -> interpretation`

The figure is the last translation, not the result by itself. Every color,
line, dot, and animation frame must map back to a named array element with a
unit or an explicit statement that it is unitless/model units.

## Tool map

| Scale or task | Main tool | Use it for | Do not claim from it |
|---|---|---|---|
| Basic calculations and data | Python, NumPy, pandas, SciPy | Arrays, tables, ODEs, statistics, parameter sweeps | Biological validity merely because code ran |
| Reproducible exploration | JupyterLab | Prediction, code, result, and interpretation in one document | Reproducibility without a clean restart-and-run |
| Single simplified neurons | Brian2 | Spikes, thresholds, rates, networks of point neurons | Dendritic anatomy from a point model |
| Ion-channel teaching model | SciPy | Hodgkin-Huxley gates, currents, voltage, solver checks | A fitted human cell or whole brain |
| Morphological cells | NEURON | Soma/dendrite geometry, channels, synapses, spatial voltage | Whole-brain activity from one cell |
| Reaction networks | Tellurium | Concentrations, binding, conservation, kinetic approximations | Drug exposure or molecular truth without fitted kinetics |
| Circuits | Brian2/custom Python | E/I populations, synaptic currents, spikes, seed variation | A disease, person, or clinical treatment response |
| Brain-region networks | TVB | Connectomes, delays, regional population dynamics | Individual action potentials, literal current, EEG, or fMRI unless a forward model produces that observable |
| Figures | matplotlib, Plotly | Static evidence figures and interactive inspection | Meaning from decorative anatomy alone |
| Queries and experiment records | DuckDB, JSON/CSV/NPZ | Traceable comparisons across runs | Independent samples from repeated time points |
| Baseline AI research | scikit-learn | Simple held-out baselines, preprocessing pipelines, error analysis | Generalization without a genuinely held-out test |
| Larger AI models | PyTorch/Transformers only when needed | Train or evaluate a specified model against a baseline | Expertise or scientific novelty from installing a library |
| Version and provenance | Git, manifests, requirement receipts | Preserve source, configuration, environment, and failures | Exact cross-platform reproduction from versions alone |

## Study order and proof of understanding

1. `01_neuron_and_sql.ipynb`: reproduce the threshold calculation by hand,
   query the saved table, and explain finite-window firing rate.
2. `02_ketamine_circuit.ipynb`: identify every condition, seed, control, and
   hypothetical parameter. Do not translate conductance fractions into doses.
3. `03_ion_channels.ipynb`: trace sodium activation, sodium inactivation,
   potassium activation, current sign, and voltage through one spike.
4. `04_reaction_networks.ipynb`: write the reactions and conservation laws,
   then explain why the reduced equation diverges in one regime.
5. `05_brain_regions.ipynb`: identify the weight matrix, delay information,
   state array, axes, coupled control, and numerical-convergence comparison.
6. `06_neuron_compartments.ipynb`: connect morphology, stimulation site,
   membrane voltage, attenuation, delay, and spatial discretization.
7. `07_numbers_to_brain_maps.ipynb`: map array values into anatomical
   coordinates and explain precisely what the animation does and does not show.

For each lesson, independent understanding means I can answer five questions
without copying: What is the question? What is the state variable and unit?
Which assumption did I change? Which control could falsify my explanation? What
claim remains outside the model?

## From numbers to a legible picture

Use this visual grammar:

| Data object | Honest visual | Question it answers |
|---|---|---|
| `value[time]` | Line plot | When and how strongly did one quantity change? |
| `value[time, location]` | Heatmap or colored anatomy | Where and when did a modeled state change? |
| `weight[target, source]` | Matrix or network edges | Which modeled locations are structurally linked? |
| spike times | Raster | Which cells fired and when? |
| concentration by species | Curves plus reaction diagram | How did material move among chemical species? |
| condition x metric x seed | Dots/intervals, not only bars | Is the result stable across repetitions? |
| predicted versus observed | Identity/scatter and residual plots | Where does the model fail against data? |

The new anatomy-aware animation performs four transparent operations: take one
row of the regional state array, place its 76 entries at the 76 saved region
coordinates, map numeric value to a fixed color scale, and advance to the next
sample. Faint lines come from the strongest structural weights. This makes the
array readable, but it does not convert the values into electrical current.

## Why there is no literal current flowing through a brain yet

The current workbench contains different scales that are intentionally
separate:

- The ion-channel and NEURON lessons use membrane voltage in mV and currents in
  defined electrophysiological units at a cell or compartment.
- The circuit lesson summarizes cell and synapse behavior over populations.
- The TVB lesson uses an abstract population state in model units at 76 brain
  regions.

Membrane mV cannot be pasted into a regional node and renamed whole-brain
current. A defensible bridge needs a population transfer function, compatible
units, a connectome with tract lengths/conduction delays, a defined stimulus,
and validation against a matching observable. EEG, MEG, fMRI, and local field
potential each require different observation or forward models.

For a real latency question, define one perturbation and one event criterion,
such as first threshold crossing relative to the source. Then show a latency
map, repeat it across parameter uncertainty, compare with zero coupling, and
check time-step stability. “Color changed later” is not enough by itself.

## Rebuild an existing model safely

1. Copy one baseline notebook or script into a newly named experiment. Never
   overwrite the saved baseline.
2. Write the question, prediction, primary metric, falsifier, control, and
   stopping rule before changing code.
3. Locate the equation, parameter, initial condition, input, and numerical
   solver separately. Change one category first.
4. Run the baseline and one changed condition with identical random seeds and
   numerical settings.
5. Add a negative control and a finer-step or finer-space comparison.
6. Save raw arrays before plotting. Record source hash, environment, parameters,
   seed, checks, and failed runs.
7. Rebuild the figure from saved arrays in a fresh process. Point to the exact
   array dimensions represented by every axis and color.
8. Write result and boundary together. A passed software check is not a
   biological validation.

## Build my own model

Begin with a small question, not a large brain picture. Select a published
model whose equations, parameters, data provenance, and expected output are
available. First reproduce one published behavior without adding a new theory.
Only then change one mechanism and compare against the reproduced baseline.

A useful progression is:

`single mechanism -> one cell -> small circuit -> population transfer function -> regional network -> observation model`

Each arrow is a research problem. Keep both sides executable independently and
test whether the added scale predicts something the simpler model misses.

## Apply the same discipline to AI research

For AI, replace “biological mechanism” with “data-generating and learning
assumptions,” but keep the evidence chain:

`task -> dataset provenance -> split -> baseline -> model -> held-out metrics -> error slices -> interpretation`

Start with a simple baseline. Visualize label balance, missingness, leakage
risk, learning curves, confusion matrices, calibration, residuals, and concrete
failure examples. Use embeddings only as a map for exploration; distance on a
2D projection is not automatically semantic truth. Keep generated, simulated,
and observed data separate. Never tune on the final test set. Report null and
negative results alongside improvements.

## Files that preserve the work

- `research/TOOLS_AND_LESSONS.md`: detailed tool exercises and exact setup.
- `research/RESEARCH_PATH.md`: how to progress from tutorials to research.
- `research/MULTISCALE_RESEARCH_PLAN.md`: cross-scale hypotheses and stopping rules.
- `research/EXPERIMENT_001.md` through `EXPERIMENT_004_NEURON_COMPARTMENTS.md`:
  completed local experiment records and their boundaries.
- `results/`: raw arrays, configurations, checks, figures, source copies, and
  interpretation templates.
- Requirement receipts and environment folders: the current software state.

The work remains local, AI-assisted study material. Independent proficiency is
earned by reproducing, modifying, checking, and explaining the models, not by
the presence of the files.
