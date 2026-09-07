# My neuroscience tools and practice guide

Updated September 7, 2026 (America/Chicago). This extends the Desktop `SCIENCE_SKILLS_AND_PROJECTS.md`; it does not replace the older AI, security or career guides. These are local learning projects. Installing a tool or running AI-assisted code is not the same as being proficient in it.

## Where to start

Double-click **Open Neuroscience Lessons.cmd** on the Desktop. It opens JupyterLab at this workbench. Keep the terminal open while studying. If the browser does not open, use the localhost link shown in that terminal; keep its token private. Stop with Ctrl+C when finished.

Open one notebook, choose its kernel, and use Shift+Enter for one cell or Run → Run All Cells. The three new notebooks first show saved results. They do not run a new simulation unless you change `RUN_NEW` to `True` and write a prediction. Save your notes with Ctrl+S. Restart the kernel and run from the top to check that hidden notebook state is not doing the work for you.

| Notebook | Kernel | What I am studying |
|---|---|---|
| `01_neuron_and_sql.ipynb` | Science Workbench | A simple electrical neuron, tables, SQL, analytic comparison |
| `02_ketamine_circuit.ipynb` | Science Workbench | Excitatory/inhibitory circuits and hypothetical NMDA conductance changes |
| `03_ion_channels.ipynb` | Science Workbench | Sodium and potassium currents, gate variables, spike generation |
| `04_reaction_networks.ipynb` | Science - Tellurium | Binding reactions, conservation, an approximation and its limits |
| `05_brain_regions.ipynb` | Science - TVB | A network of 76 regional oscillators and delayed coupling |
| `06_neuron_compartments.ipynb` | Science - NEURON | Active soma, passive dendrite, attenuation, and spatial resolution |
| `07_numbers_to_brain_maps.ipynb` | Science - TVB | How arrays, coordinates, colors, and time become an anatomy-aware regional display |

The calculation is in `lessons/run.py`. The notebook is where I inspect it, make predictions and discuss results. The files under `results/multiscale/` are the evidence, not just screenshots.

## What was installed and what is pending

| Tool | State at this checkpoint | Where it runs |
|---|---|---|
| Python 3.13 and original scientific packages | Existing working environment preserved | `.venv\Scripts\python.exe` |
| Python 3.12.13 | Installed through uv for the extra environments | Selected by the two new environments |
| Tellurium 2.2.13.1 / libRoadRunner 2.10.0 | Installed; reaction simulation and independent-solver comparison passed | `.venv-biochem\Scripts\python.exe` |
| The Virtual Brain library 2.10.0 / tvb-data 3.0.0 | Installed; regional model, deterministic repeat and finer-step run completed | `.venv-tvb\Scripts\python.exe` |
| Three additional Jupyter kernels | Registered | Science - Tellurium; Science - TVB; Science - NEURON |
| NEURON 9.0.2 | Official installer digest matched; native HOC and Python 3.10/3.13 bindings passed; a two-compartment HH propagation check passed | `C:\nrn`; `.venv-neuron\Scripts\python.exe` |
| TVB framework web application / surface geodesic extension | Not installed; not needed by the regional notebook | Later only if the project needs them |
| Extra GPU/HPC tooling, custom NMODL compiler, LFPy | Not installed in this step | Later, after a selected published model requires them |

Tellurium caveat: `uv pip check` reports incompatible internal wheel tags for Antimony (`cp313`) and phrasedml (`cp39`) inside the installed Windows packages. Both import under Python 3.12, and Antimony translated the tested model successfully. This is a remaining packaging warning, not a claim that every Tellurium feature has been validated. Do not edit wheel metadata to silence it. COMBINE/SED-ML/phrasedml workflows need separate tests before use. TVB's package dependency check passed. It warns about unavailable surface geodesics and an absent hemispheres field in the bundled connectome; the regional demo does not use either. Its deterministic integrator also emits an upstream random-state warning; the repeat output is identical.

The NEURON download is `C:\Users\jojo\Downloads\nrn-9.0.2.w64-mingw-py-310-311-312-313-314-setup.exe`. SHA-256: `f5bb285c9efa330f4d1ae67885755443b363e829c50e9ffa15f6b9cba44114ce`, matching the official GitHub 9.0.2 asset digest. The executable is not Authenticode-signed, so the digest and official release provenance matter. Windows PyPI wheels are unavailable for this release; `.venv-neuron` links to the installed `C:\nrn\lib\python` package. The working SciPy channel lesson remains a separate implementation, not a NEURON result.

## Reproduce the working experiments

Open PowerShell. These commands use explicit interpreters, so activating an environment is unnecessary:

```powershell
cd C:\Users\jojo\Projects\science-workbench
.\.venv\Scripts\python.exe lessons\run.py channels --prediction "Write my prediction here"
.\.venv-biochem\Scripts\python.exe lessons\run.py reactions --prediction "Write my prediction here"
.\.venv-tvb\Scripts\python.exe lessons\run.py regions --prediction "Write my prediction here"
```

Replace the example text with your actual prediction. Each command runs its fixed tutorial protocol once. The printed path contains the configuration, exact source copy/hash, package versions, CSV/NPZ data, plot, metrics, checks, and a blank interpretation template. A failed check raises an error and leaves the run in place. A crash can leave a manifest marked `started`; that is not a completed result. A completed check suite establishes only the properties it tested.

For a fresh installation **in a new copy of the workbench**, with Python/uv available:

```powershell
uv venv --python 3.13 .venv
uv pip install --python .venv\Scripts\python.exe -r requirements-lock.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name science-workbench --display-name "Science Workbench"
uv python install 3.12.13
uv venv --python 3.12.13 .venv-biochem
uv pip install --python .venv-biochem\Scripts\python.exe -r requirements-biochem-lock.txt
uv venv --python 3.12.13 .venv-tvb
uv pip install --python .venv-tvb\Scripts\python.exe -r requirements-tvb-lock.txt
.\.venv-biochem\Scripts\python.exe -m ipykernel install --user --name science-biochem --display-name "Science - Tellurium"
.\.venv-tvb\Scripts\python.exe -m ipykernel install --user --name science-tvb --display-name "Science - TVB"
uv venv --python 3.13 .venv-neuron
uv pip install --python .venv-neuron\Scripts\python.exe -r requirements-neuron-lock.txt
.\.venv-neuron\Scripts\python.exe -m ipykernel install --user --name science-neuron --display-name "Science - NEURON"
.\.venv-neuron\Scripts\python.exe verify_neuron.py
```

Do not recreate an existing environment just to follow this example. The original `.venv` uses Python 3.13 and `requirements-lock.txt`, as described in the README. The new lock files record resolved package versions, not cryptographic wheel locks; cross-platform reproduction still needs testing. Original installation requests were `tellurium ipykernel matplotlib` and `tvb-library tvb-data ipykernel matplotlib`. All computations here are local CPU work, with no paid API or cloud job.

## The tool-by-tool practice sequence

### 1. Python: express a calculation I understand

Start in a new notebook using Science Workbench. Learn names, numbers, lists, dictionaries, indexing, `for`, `if`, functions, imports and errors. Then file paths and JSON. Do not start by memorizing every language feature.

Exercise: make a list `[0, 4, 1, 0]` of spike counts, label the four conditions, and print a sentence for each. Write a function that turns spikes in a 50 ms window into Hz. Four spikes / 0.05 seconds = 80 Hz; that differs from four spikes over the full 100 ms simulation. Always state the counting window.

Proof I learned it: write this in a blank notebook without copying. Explain every line and handle a zero-length window with a clear error. Next, read `manifest.json` with `json.loads` and explain what a dictionary key is. An AI-generated function I cannot explain is practice material, not evidence of mastery.

### 2. JupyterLab: make the notebook reproducible

A cell can depend on a variable created earlier even if I later delete that cell. This hidden state is a common source of misleading success. Restart the kernel, run from the top, and check `sys.executable` before trusting a result. Markdown cells are for predictions and interpretations; code cells perform computations.

Exercise: add a Markdown prediction, run the saved-example cells, explain one axis, and save. Then restart and repeat. Learn interrupt, restart, kernel selection and relative paths. Do not expose the server beyond localhost or share its access token.

### 3. NumPy: work with arrays without confusing dimensions

An array is a structured block of numbers. For the ion-channel CSV, rows are times and columns are measurements. For TVB traces, one dimension is time and another is brain region. Averaging over the wrong axis changes the question.

Exercise: load a CSV with `np.genfromtxt(..., delimiter=',', names=True)`. Find maximum voltage and the time where it occurs. For TVB, load `regional_traces.npz`, print each shape, and compare `coupled.mean(axis=0)` (time average per region) with `coupled.mean(axis=1)` (region average per time). Match one entry by hand.

Proof: explain axis 0 versus axis 1 without relying on the picture. Do not average different physical units into one number.

### 4. pandas: turn outputs into a checkable table

Use `pd.read_csv` on a saved channel trace. Learn column selection, filtering, grouping, missing values and joins. Preserve condition, units and run ID in tables. Time samples from the same run are correlated; 4,001 rows do not mean 4,001 independent experiments.

Exercise: select times from 10 through 60 ms, count threshold upcrossings, and compare against `metrics.json`. Explain why counting every sample above zero overcounts spikes. Review ten rows manually.

### 5. SQL / DuckDB: ask explicit questions of the records

Use the existing Science Workbench kernel, `import duckdb`, then query a copied path to a CSV:

```python
duckdb.sql("SELECT MAX(voltage_mV) AS peak_mV FROM read_csv_auto('results/multiscale/YOUR_RUN/baseline.csv')").show()
```

Replace `YOUR_RUN` with an actual directory. Learn SELECT, WHERE, GROUP BY, JOIN, NULL and keys before window functions. Exercise: retrieve the baseline peak and pulse-window average, then compare with NumPy. Later make a run-summary table keyed by run ID; do not join by a non-unique label and accidentally multiply rows.

### 6. matplotlib and Plotly: make a measurement readable

matplotlib creates the saved scientific figures. Plotly is available in the original environment for hover/zoom exploration. Start with line plots, labels, legends, axes limits and units. A line is not evidence unless I know where its numbers came from.

Exercise: redraw only the first spike between 10 and 16 ms using a saved CSV. Put voltage above sodium/potassium currents with a shared time axis. Add a caption saying which model and run produced it. In Plotly, use the same saved table, not a separately recomputed result. Never call model-unit TVB state “mV” or “EEG”.

### 7. SciPy: solve equations and test numerical error

An ODE gives the rate of change, not the finished curve. `solve_ivp` repeatedly estimates the state forward in time. The ion lesson uses DOP853, tight tolerances, and separate solves at pulse boundaries. The independent reaction calculation uses LSODA.

Exercise: solve `dy/dt=-y`, starting at 1. Compare with `exp(-t)`. Vary the tolerances and maximum step separately. Then read `hh_trace`: identify initial conditions, the derivative, output times, pulse boundaries and the success check. Smaller plotted intervals alone do not guarantee smaller integration error.

Proof: explain the difference between model error (wrong equations for the biology) and numerical error (imperfect solution of the chosen equations). A tiny numerical error does not validate the biology.

### 8. SymPy and mathematics: derive one result before simulating

SymPy manipulates symbolic expressions; it does not decide whether an equation represents a real cell. Start with units, algebra, derivatives and linear ODEs. Then matrices, eigenvalues, stability and parameter sensitivity.

Exercise: derive `V(t)=E_L+I*R+(V(0)-E_L-I*R)*exp(-t/tau)` for a passive membrane. Check the initial value and long-time limit. Independently cancel terms in the reaction conservation laws. Use symbolic software only after writing the intended calculation on paper.

### 9. Brian2: go from a cell to a circuit

Brian2 supplies units, state equations, synapses and spike recording. Start with notebook 01, then 02. Understand the existing leaky integrate-and-fire simplification before using the channel model: the LIF model resets after crossing a threshold, whereas HH generates its spike from continuous gate/voltage dynamics.

Exercise: locate `NeuronGroup`, equations, monitors and the simulation clock in the original code. Explain one AMPA, NMDA and GABA-A contribution from the model card. Change one parameter with a fixed seed and preserve the baseline. Your previous size experiment already showed that 1/N weight scaling did not make all firing results size-invariant.

Proof: distinguish excitatory/inhibitory classification, receptor kinetics and membrane spiking. A hypothetical reduction in NMDA conductance is not a ketamine dose-response curve.

### 10. Hodgkin–Huxley with SciPy: the ion-channel lesson available now

The cell membrane stores charge like a capacitor. Channels let ions carry current according to conductance and an electrochemical driving force. This analogy explains the circuit equation; it does not include every biological process.

```text
Cm dV/dt = Iexternal - INa - IK - IL
INa = gNa * m^3 * h * (V - ENa)
IK  = gK  * n^4     * (V - EK)
IL  = gL            * (V - EL)
dx/dt = alpha_x(V) * (1-x) - beta_x(V) * x
```

V is mV; time is ms; conductance density is mS/cm²; current density is µA/cm²; capacitance density is µF/cm². Each term in the voltage equation has matching units. A 10 µA/cm² input into 1 µF/cm² would initially change voltage by 10 mV/ms if all other currents were absent. They are not absent in the real calculation.

`m` is sodium activation, `h` is sodium availability/inactivation, and `n` is potassium activation. They lie between 0 and 1; `m³h` and `n⁴` set effective conductance fractions. They are phenomenological gate variables, not literal counts of three or four doors I observed. The rates and removable singularities are visible in `hh_rates`. Resting gates start at `alpha/(alpha+beta)` at -65 mV.

For example, at -65 mV, alpha_m is about 0.224/ms and beta_m is 4/ms, giving m∞≈0.053. Larger m opens the modeled sodium conductance; smaller h makes less available. Depolarization can increase sodium activation rapidly while potassium activation responds more slowly. The combined dynamics, not an imposed reset, generate the spike and recovery.

Read the top plot to count spikes; inspect currents to explain how they occur; inspect gates to explain why the currents change. Here the full, half and zero sodium conditions produce 4, 1 and 0 spikes. Half the conductance did not mean half the spikes. The no-input control is silent. These are squid-axon-derived teaching dynamics at 6.3°C, not a calibrated human cortical neuron. Reversal potentials are fixed; the model does not explicitly maintain ion gradients with ATP-consuming pumps, track ion concentrations, or model drug binding.

Exercise: reproduce one rate calculation by hand, then try `hh_trace(current=8, sodium_scale=1)` in a scratch notebook after writing a prediction. Save the modified protocol before treating it as a reportable experiment. Later, implement a passive membrane independently and compare with the analytic solution.

### 11. NEURON: morphology and spatial compartments

NEURON represents a branching cell with cable sections and computational segments. A soma and dendrite can have different voltages, ion channels and synaptic inputs. A segment is a spatial approximation, not automatically an individual biological cell. Built-in `hh` uses squid-derived sodium/potassium/leak dynamics; importing it does not create a human pyramidal cell.

NEURON 9.0.2 is installed and `verify_neuron.py` now verifies `from neuron import h`, native HOC startup, an active soma, a passive 200 µm dendrite, current injection, and propagated voltage. The fixed run produced 801 samples over 20 ms, a 33.7165 mV soma peak, and an 18.0101 mV dendritic-tip peak. These values verify software integration and qualitative propagation only; they are not fitted biological evidence.

The bundled MinGW/NMODL toolchain also compiled `mechanisms\linear_leak.mod` into `nrnmech.dll`, and Python loaded and inserted the resulting `linearleak` mechanism. Rebuild it from the `mechanisms` directory with `C:\nrn\bin\nrnivmodl.bat`. Generated C++, object, and DLL files are ignored by Git; the `.mod` source is the reproducible artifact.

First planned exercise: create a passive soma and dendrite, inject a small current, and plot voltage at the soma, midpoint and dendritic tip. Predict attenuation. Double spatial resolution with odd `nseg` values (for example 11 to 21), halve dt, and compare the measured attenuation. Only then add active channels. NEURON uses S/cm² and mA/cm² for built-in channel densities, whereas this SciPy lesson uses mS/cm² and µA/cm²: a factor of 1,000 matters.

For the cross-simulator check, explicitly match leak reversal: our tutorial uses -54.387 mV while NEURON's standard `hh` default is -54.3 mV. Match temperature, area/current conversion, initialization and solver settings too. An unexplained disagreement is not a biological discovery.

### 12. Tellurium / Antimony / RoadRunner: chemical systems

Tellurium is the environment; Antimony is the readable model language; RoadRunner solves the resulting reaction equations. They are related tools, not three unrelated apps I need to open. Use notebook 04 with Science - Tellurium.

The model has free enzyme E, substrate S, bound complex ES and product P. Binding has rate `k1*E*S`, unbinding `km1*ES`, and conversion `kcat*ES`. Write these out:

```text
dE/dt  = -k1*E*S + km1*ES + kcat*ES
dS/dt  = -k1*E*S + km1*ES
dES/dt =  k1*E*S - km1*ES - kcat*ES
dP/dt  = kcat*ES
```

The totals E+ES and S+ES+P must stay constant. This is an excellent debugging check: if a reaction creates an unaccounted molecule, the code or equation is wrong. The example interprets concentrations in µM and time in seconds in a fixed unit-volume compartment; no experimental kinetic constants or certified SBML unit validation are claimed.

The reduced equation is `dS/dt=-Vmax*S/(Km+S)`, with `Vmax=kcat*Etotal` and `Km=(km1+kcat)/k1`. Its free-substrate bookkeeping omits explicit bound substrate. Compare full and reduced product curves, especially the initial transient and abundant-enzyme condition. Our controls compare the full model against independently written SciPy equations and verify conservation. These checks are separate from whether the reduced approximation is accurate.

Proof: derive the conservation identities and explain the 0.139 versus 5.077 µM discrepancies. Then reproduce an actual published biochemical model unchanged before proposing a BDNF-related extension. Do not rename E to “BDNF” and present invented rates as biology.

### 13. The Virtual Brain: interactions among regions

TVB is the regional scale, not a more detailed version of the single cell. The current example has 76 regions, each with two abstract state variables. Connections determine weighted, delayed input between them. It has neither 76 anatomical cells nor a full set of molecules inside each region.

Use notebook 05 with Science - TVB. The Generic2dOscillator uses a fast-state/recovery-state system with polynomial equations. The coefficients are saved in `oscillator_parameters.json`; the source is in TVB's `simulator/models/oscillator.py`. We set `a=2` for the oscillatory teaching configuration. V remains in model units, not calibrated millivolts.

The supplied connectome gives weights and tract lengths. Delays use length/speed, with speed 3 mm/ms here. We divide weights by the largest row sum, use identical initial histories, and compare coupling 0 and 0.02. Initial history is held constant before time zero. The temporal monitor averages 1 ms windows; a 0.1 ms integration step is not a 1 ms integration step. The first 100 ms of simulated time is excluded from summary metrics.

Exercise: find one region label and its strongest incoming connections in the saved matrix. Calculate a weighted sum of states. Compare regional differences with coupling off and on. More similarity is not inherently healthier; this example cannot establish illness, recovery or emotion. A structural connection matrix and a correlation matrix of outputs are different objects.

Proof: explain the region count, state count, coupling, delays, time step, initial conditions and what the monitor measures. Repeat at a smaller dt before making a physiological interpretation. Next experiment should vary an explicit hypothesis with several initial conditions and retain a no-effect outcome; one initial state is not a robust population conclusion.

### 14. Git, environments and tests: keep the evidence traceable

Use `git status --short` and `git diff -- README.md` to inspect changes. Do not stage the entire workbench blindly: it already contains earlier local work. Commit only reviewed source/docs and selected small evidence, never `.venv` folders, private notes, credentials or restricted data. Nothing in this setup publishes to GitHub.

Exercise: make one clearly explained change in a separate copy/branch, run the relevant tests, review the diff, and record the run ID. The manifest saves the source hash and package versions, but exact reproducibility also depends on platform and numerical libraries. Learn to read a traceback and distinguish missing package, wrong kernel, model failure and failed expectation.

### 15. Statistics, scikit-learn and later ML

The original environment has scikit-learn. It is not needed to produce today's mechanistic simulations. Learn variance, effect size, confidence intervals, confounding, repeated measurements and held-out testing first. PyTorch/large models are not prerequisites for ion-channel modeling.

Later exercise: fit a simple surrogate to simulator input/output pairs and test on parameter ranges excluded from training. Compare with a simple interpolation/baseline. A surrogate reproduces a simulator, including its errors; it does not validate the simulator against a biological brain. Randomly splitting adjacent time rows can leak nearly identical examples across train and test.

## A repeatable study session

Spend the first session on notebook 03 only: read the plot, calculate one gate value, explain current signs, predict one change, run it, and write what disagreed with the prediction. In later sessions, learn reactions and regional coupling. Keep one primary question per session, not fifteen new libraries.

I am ready to claim hands-on project use when I can start from a blank notebook, reproduce the calculation, explain units and assumptions, catch a planted error, and describe a result that did not support my expectation. Until then, “self-learning neuroscience simulation with AI-assisted implementations” is the honest description.

## References

- [NEURON built-in HH source and parameter conventions](https://github.com/neuronsimulator/nrn/blob/9.0.2/src/nrnoc/hh.mod).
- [NEURON scripting tutorial](https://www.neuronsimulator.org/en/9.0.0/tutorials/scripting-neuron-basics.html).
- [SciPy solve_ivp documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html).
- [Tellurium installation](https://tellurium.readthedocs.io/en/latest/installation.html) and [Antimony language](https://tellurium.readthedocs.io/en/latest/antimony.html).
- [TVB source, installation and licenses](https://github.com/the-virtual-brain/tvb-root); [TVB data repository](https://github.com/the-virtual-brain/tvb-data).
- The existing [evidence report](REPORT.md), [model card](MODEL.md) and [research path](RESEARCH_PATH.md) cover the earlier circuit and evidence limitations. Today's tutorials do not replace those sources or validate their clinical hypotheses.
