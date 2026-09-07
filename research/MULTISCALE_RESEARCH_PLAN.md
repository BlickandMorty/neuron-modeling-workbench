# A more detailed brain project, built one testable part at a time

Checkpoint: September 6, 2026. Local development, not a public clinical model. This plan extends [RESEARCH_PATH.md](RESEARCH_PATH.md) and uses the existing [evidence review](REPORT.md). It is a research design, not a claim that the planned mechanisms have already been implemented.

## The project question

How do changes at a receptor or cell change a circuit's response to an input, and which effects remain when we change the model's resolution or assumptions?

For now, this is more workable than “simulate the PTSD brain and every ketamine effect.” We can measure input/output changes, test alternative mechanisms and keep failures. A PTSD diagnosis is not one universal set of electrical parameters. A later disease-related comparison needs an operational definition and suitable observed data, not just a label on a slider.

## What each scale means

| Scale | State being modeled | What a useful experiment could measure | Present status |
|---|---|---|---|
| Ion channels | Voltage and activation/inactivation gates | Spike waveform, threshold, refractory behavior, conductance sensitivity | Working SciPy HH tutorial; not human-cell calibrated |
| Cell geometry | Voltage at positions along soma/dendrites | Attenuation, local integration, location-dependent response | NEURON 9.0.2 installed; fixed soma/dendrite lesson and spatial-resolution check completed |
| Synapses / cell types | Receptor gating, subtype-specific spikes, connections | Input responsiveness, firing distributions, oscillatory changes | Existing generic E/I circuit; subtype-specific replication pending |
| Chemical reactions | Molecule concentrations and bound complexes | Conservation, reaction time course, approximation error | Generic Tellurium enzyme tutorial; no BDNF kinetics |
| Brain regions | Population-level dynamic states and long-range input | Propagation, regional trajectories, coupling sensitivity | Working 76-region TVB tutorial; no patient fit |
| Measurement | Mapping hidden states to an observable | Current-clamp voltage, LFP/EEG/MEG/BOLD or a behavioral response | Voltage/current/region-state plots only; no validated forward model |
| Learning and clinical time course | Task-specific memory/learning variables and observed outcomes | Extinction, generalization, return of a response, measured symptoms | Proposed; no implemented trauma learning or clinical predictor |

The rows are not a chain we can automatically connect. A chemical concentration does not become a synaptic conductance unless we specify and justify that relationship. A regional model's V is not the single-cell voltage V merely because both use the same letter.

## What detailed cells would add

A point neuron assumes all of its membrane shares one voltage. A cable model allows current to flow between neighboring compartments. A schematic compartment equation is:

```text
C_i dV_i/dt = I_external_i - I_ion_i + sum_j g_axial_ij * (V_j - V_i)
```

Here capacitance, current and axial conductance must use consistent total quantities; do not mix total nA with current density without converting membrane area. Cell diameter, length and axial resistivity affect how much current spreads. Synapses at different dendritic locations can affect the soma differently. Adding sodium, potassium, calcium or other channels adds equations and parameters, not just detail in a picture.

The next model should start passive so we can check cable behavior, then add one justified active mechanism. Check both time resolution and spatial resolution. Eventually use a published morphology/channel model with recorded responses. Do not invent a large branched “human neuron” solely to make the visualization more impressive.

## The next experiments and their stopping points

### A. Learn and independently reproduce the channel result

Question: why did half sodium conductance produce one spike rather than half of four?
Use the saved baseline, half-sodium and no-sodium traces. Inspect the m/h/n gates, driving forces and potassium current. Primary deliverable: Jordan's own derivation, one independently written gate calculation and an interpretation of the altered firing pattern. Stop when the calculation can be rebuilt from a blank notebook and its limits explained. Do not add a drug label.

### B. Passive cable, then one active dendrite

The initial NEURON milestone is now complete and recorded in [Experiment 004](EXPERIMENT_004_NEURON_COMPARTMENTS.md). The fixed active-soma/passive-dendrite model passed its propagation and spatial-resolution checks. The next step is not a larger decorative morphology: reproduce a published cell model with traceable morphology, channels, parameters, and an experimental observable.

### C. Replicate a cell-type-specific published result

Candidate: [Rademacher et al. (2025)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1013118), with [public code](https://github.com/jessierademacher/Ketamine_E-I). Their model reproduces a gamma increase under some NMDA manipulations but does not reproduce the observed aperiodic-slope change. Human MEG/clinical data are not public. That makes a selected simulation figure a possible replication target, not a full participant-data replication.

Before execution: inspect licensing, dependencies, code revision, compute cost and the exact target figure. Record original parameters and observable. First reproduce unchanged; only then compare a subtype-specific intervention with an equally sized non-specific intervention. Match computational outputs to the paper's observable rather than rename a firing-rate spectrum as MEG. Preserve the failure to match another observable. No extra intervention is implemented at this checkpoint.

### D. Separate exposure, receptor effect and downstream change

An eventual exposure model might have concentration dynamics and a receptor-effect model, but those require traceable route/formulation/species-specific data. Current fractional conductance changes are only parameters, not doses. Receptor occupancy alone may not capture state/use-dependent channel blocking or all targets. First decide which measured response will constrain the model. Stop if the parameters cannot be identified from available data; show ranges or competing explanations instead of a fitted certainty.

### E. Biochemistry with a published kinetic model

Use the generic enzyme lesson to learn stoichiometry, conservation and solver verification. Then select one published signaling model with an accessible parameter table and a defined cellular compartment. Reproduce one time course before introducing any ketamine/BDNF hypothesis. The existing evidence review separates molecular findings, later plasticity, species and inconsistent clinical translation. Do not compress them into an obligatory “block NMDA → raise BDNF → repair brain” sequence.

Success is a traceable reaction model plus a defensible comparison. Failure includes missing kinetics, equally good incompatible mechanisms or an approximation that diverges. Such a failure can set the scope of a useful paper-quality evidence audit without fabricating a simulation.

### F. Regional robustness, not simply a larger graph

The present TVB example uses one initial-state seed, two coupling levels and generic identical regional equations. A next fixed experiment can compare a small prespecified coupling grid across several initial histories, including zero coupling. Primary metric: trajectory differences and between-region dispersion after a chosen transient, with convergence checks. Do not call dispersion a clinical score or infer connectivity causality from output correlation.

Before regional specialization, choose a connectome with clear source/atlas provenance and an observable to compare against. More regions add cost but do not automatically add cellular detail. Stop after the fixed grid even if differences stay small; investigate the model regime rather than keep tuning toward a desired picture.

## How to connect two scales responsibly

1. Specify what leaves the first model: for example, a firing-rate response curve under controlled input, not a screenshot.
2. Specify what enters the second model: a calibrated transfer-function parameter with the same meaning and compatible units.
3. Estimate the mapping on a training set of conditions and test it on held-out conditions.
4. Propagate parameter uncertainty. Compare the linked model with a simpler unlinked baseline.
5. Keep each component executable alone. A combined model must earn its complexity by predicting something the simpler model misses.

This is where useful research can emerge: which assumptions survive a change of scale, which do not, and what evidence would distinguish explanations. The current three tutorials are separate foundations, not an already integrated multiscale brain.

## What an interpretable visualization should show

- Cell: shape and stimulation site beside voltages/currents, with time and spatial resolution stated. Use the checked NEURON soma/dendrite result or the actual HH three-panel plot rather than a decorative brain.
- Reactions: reaction diagram plus concentration curves and conserved totals. A molecular name requires a supported model; labels are not evidence.
- Circuit: raster, input timing, rates and specific measured current. Show controls and seed variability.
- Regions: structural weights, region/time heatmap, and a few labeled traces. Clearly distinguish structural connections from functional correlation.
- Evidence: observed human/animal data in a separate panel from simulations, using matching observables only.

Read the current figures before adding a 3D viewer. If we later build ResearchBox, it should index these actual run manifests and let a user open the source, assumptions, data and interpretation. It should not imply that a brain animation is a validated biological model.

## Resume and public boundary

Publishing this learning work does not turn the tutorials into novel findings. The accurate description remains: “I am learning neuroscience modeling through reproducible cell, reaction-network and regional simulations. I use AI assistance for implementation and keep the assumptions, controls and failed comparisons with the results.” Only claim independent skills as the exercises are actually completed.
