# From a teaching circuit to a scientific modeling project

September 7 extension: the [multiscale plan](MULTISCALE_RESEARCH_PLAN.md), [tool lessons](TOOLS_AND_LESSONS.md), [multiscale results](EXPERIMENT_003_MULTISCALE.md), and [NEURON verification](EXPERIMENT_004_NEURON_COMPARTMENTS.md) now add a SciPy channel model, Tellurium reaction model, TVB regional example, and a checked NEURON soma/dendrite simulation. References below to not-yet-installed tooling describe earlier checkpoints and are superseded by these additions. Published microcircuit replication and biological validation remain pending.

## What you are building, and what you are not

You are building a mathematical model in Python, not merely a visualization. The notebook is the experimental console: the equations live in `circuit_lab.py`, inputs are explicit configurations, the simulator integrates the equations, and the plots display saved numerical outputs. You can inspect, derive, replace, and test those equations yourself.

The present implementation is a local circuit with 80 excitatory and 20 inhibitory cells by default. It is **not a comprehensive brain**. Choosing 250 or 500 cells repeats the same kind of circuit at another size; it does not add brain anatomy, cell diversity, trauma learning, autonomic regulation, or drug metabolism. Those require different model components and independent evidence.

## Do real researchers use small models?

Yes. Model scope follows the question, not a minimum impressive neuron count. Researchers may reuse published models, adapt them with documented changes, derive reduced equations, or build a new mechanism when existing models cannot answer the question. Reproducing an existing result before extending it is a strong starting point.

Three concrete references:

- The official [Brian2 Wang example](https://brian2.readthedocs.io/en/2.10.1/examples/frompapers.Wang_2002.html) uses 2,000 neurons, with selective decision pools. Our implementation borrows equations and parameter scales but omits those pools; it is not an exact replication.
- [Rademacher et al. (2025)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1013118) used a detailed 1,000-neuron cortical microcircuit, including several inhibitory cell types, NEURON and LFPy. It reproduced a gamma increase but not the observed aperiodic flattening. Its scope is a cortical microcircuit, not a full brain. Public code is available; the human MEG and clinical recordings are restricted.
- [The Virtual Brain (Sanz Leon et al., 2013)](https://www.frontiersin.org/journals/neuroinformatics/articles/10.3389/fninf.2013.00010/full) models large-scale brain-network dynamics with connectivity and population-level neural mass/field models. A node can represent a population or region rather than one neuron. Whole-brain coverage is not the same as cellular or molecular completeness.

These are different scientific resolutions, not a ladder on which every larger model is automatically better. A simple model can reveal a mechanism cleanly; a detailed model can test features that the simple one cannot represent. Both need validation appropriate to their claims.

## A model-selection map for your long-term question

| Question | Representation worth considering | Evidence needed before interpreting it biologically |
|---|---|---|
| How can reduced NMDA input alter local excitation and inhibition? | Spiking E/I circuit: current work | Published equations, numerical controls, measured firing/current comparisons |
| Which inhibitory subtypes explain spectral changes? | Published cell-type-specific microcircuit | Cell physiology, connectivity, matched acquisition/forward model, spectral comparisons |
| How do changes propagate between brain regions? | Regional neural mass/field network with structural connectivity | Atlas/connectome provenance, coupling/delays, appropriate EEG/MEG or BOLD observation model |
| How does exposure change with time? | Separate pharmacokinetic/pharmacodynamic module | Formulation/route-specific concentration-time and target-effect data; parameter uncertainty |
| Does a learned response persist, generalize, extinguish, or return? | Explicit learning/task model | Task data, learning rule, competing explanations, held-out behavioral measurements |
| How do autonomic responses change alongside brain activity? | Coupled brain/body state model | Time-aligned physiological recordings and justified coupling; not a vague “reset” variable |
| What sustains changes over days? | Slower plasticity model | Species- and context-specific longitudinal measurements; no assumed obligatory recovery chain |

This table is a proposed research architecture, not a list of implemented features. Do not bolt all the rows together before individual components are testable. Greater biological coverage increases the number of assumptions and the risk of non-identifiability: different mechanisms can produce similar plots.

## The mathematics underneath the workflow

In general, write the hidden system state as a vector x and its measurements as y:

$$\dot{x}=f(x,u,\theta),\qquad y=h(x,\phi)+\epsilon.$$

Here x might contain voltages and synaptic gates; u contains inputs; theta contains time constants and coupling strengths. The observation model h translates state into the particular quantity an experiment measures; phi contains its parameters and epsilon represents measurement noise. A spike-count rate is not automatically an EEG measurement. Adding an EEG or BOLD observation model is a substantive scientific step, not renaming an axis.

For your present circuit, the NMDA intervention changes one part of theta: effective conductance = baseline conductance × (1 − b). It is **not yet a mathematical model of ketamine exposure, all drug targets, or clinical response**. A separate exposure model would be needed to relate concentration over time to conductance; no such calibration is currently available in this workbench.

The researcher loop is: specify a measurable question → choose equations and evidence → record a prediction and controls → simulate → compare like-for-like observables → examine failures → change one justified assumption. Hold data back when fitting parameters so matching the fitting data is not your only test.

## Why test 100, 250 and 500 cells?

The interface now offers these sizes under Advanced. `python size_sensitivity.py` runs a fixed three-size protocol across four conditions and three seeds, reusing integrity-checked matching runs where available. It records both reuse and newly computed results. It does not silently replace the 100-cell example.

In this model, recurrent weights scale approximately as 1/N for the presynaptic population. If independent inputs each have mean mu and variance sigma², the total input J = (w0/N) sum(Xi) has mean w0 mu but variance w0² sigma²/N. Thus equal mean coupling does not imply equal fluctuations. Derive those two identities; then explain why correlated recurrent activity violates the independence assumption. This is exactly the kind of mathematical reasoning you can own.

The experiment tests post-input mean firing, with seed variability shown separately. Size differences larger than max(2 Hz, 25% of the 100-cell mean) are flagged descriptively. That threshold was specified before the larger runs, but the baseline had already been inspected. It is not a hypothesis-test p-value or a biological tolerance. A non-flagged result would not establish convergence of spectra, state transitions, or a human brain. Same seed numbers at different sizes do not generate identical input realizations.

## Concrete milestones and stopping gates

1. **Current release:** understand one circuit, its equations, four comparisons and saved evidence. Explain a null result. Do not label the hypothesis circuit a diagnosed PTSD brain.
2. **Replication:** select one published model and one figure, record the exact code revision, license, environment and target metric. Reproduce it unchanged before adding your hypothesis. The Wang example is a tractable starting candidate; the ketamine-specific Rademacher model is more detailed and needs a separate dependency/runtime assessment. Neither has been exactly replicated here.
3. **Empirical comparison:** choose a genuinely accessible dataset or permitted published summary data, define the observable and preprocessing, and specify the discrepancy measure before tuning. Public code does not imply permission to access restricted participant data. Never label simulated outputs as real recordings.
4. **One mechanistic extension:** justify a cell subtype, receptor effect or learning rule from evidence, then compare the extended model with the simpler one on held-out outcomes. Preserve a worse fit or ambiguous result.
5. **Regional brain model, if the question demands it:** assess The Virtual Brain and a suitable public connectome in a separate environment; document regional resolution, delays, coupling and observation model. Validate baseline network behavior before adding an explicitly hypothetical drug perturbation. No whole-brain package or patient data has been installed here.

Your “automatic physiological patterns” idea can stay as a research question. To test it, replace the phrase with a task and measurable persistence/generalization/return of a response, and distinguish acute disruption from later learning or symptom change. The model must be able to show no improvement.

## Where you work each day

- **JupyterLab:** calculate, plot, write predictions and interpret experiments. Start with the original `02_ketamine_circuit.ipynb`, Run → Run All Cells; the executed copy is an archive, not a live widget session.
- **Python modules / VS Code:** edit equations and analysis functions. Start with NumPy, SciPy, pandas, plotting and Brian2; advanced syntax is secondary to understanding the calculation.
- **Terminal in the project environment:** run tests and fixed experiments. The Desktop launcher already selects the project's Python environment; no extra language is needed for this release.
- **Research folder:** inspect the source-linked evidence, assumptions, disagreements and learning guide.
- **Results folders:** each run's configuration, raw arrays, metrics and interpretation. Git can track code and selected lightweight artifacts later; nothing is automatically published.

AI assisted this implementation. A defensible portfolio contribution is the experiment you can explain, reproduce, criticize and extend—not a claim that you reconstructed a complete brain.
