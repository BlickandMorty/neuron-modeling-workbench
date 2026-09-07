# Experiment 004: NEURON compartments and installation verification

Date: September 7, 2026
Status: completed local teaching and software-verification run

## Question

Can the official Windows NEURON installation run through native HOC, Python,
Jupyter, and the NMODL compiler, and does a simple active-soma/passive-dendrite
model show checked voltage propagation?

## Provenance and setup

- NEURON 9.0.2 official Windows release asset
- Installer SHA-256: `f5bb285c9efa330f4d1ae67885755443b363e829c50e9ffa15f6b9cba44114ce`
- Install location: `C:\nrn`
- Python environment: `.venv-neuron`, Python 3.13
- Jupyter kernel: **Science - NEURON**
- Notebook: `06_neuron_compartments.ipynb`
- Reusable verifier: `verify_neuron.py`

The release does not provide a Windows PyPI wheel. The isolated environment
therefore uses the Python package shipped by the official Windows installer.

## Fixed model

The model uses a 20 µm by 20 µm soma with NEURON's built-in `hh` mechanism and
a connected 200 µm by 2 µm passive dendrite. A 0.5 nA, 1 ms current pulse begins
at 5 ms. Voltage is recorded at the soma, dendritic midpoint, and dendritic tip
for 20 ms. The spatial check compares dendritic `nseg=21` with `nseg=41` while
holding `dt=0.025 ms` fixed.

## Results

- Samples: 801
- Soma peak: 33.1574 mV
- Dendritic midpoint peak: 21.3434 mV
- Dendritic tip peak: 18.1597 mV
- Soma-to-tip peak attenuation: 14.9977 mV
- Maximum tip-trace difference after spatial refinement: 0.0334 mV

All four predefined checks passed: the active soma spiked, the tip depolarized,
the tip peak stayed below the soma peak, and the refinement difference remained
below 1 mV. Raw voltage, metrics, checks, and the figure are in
`results/neuron_compartments/`.

## Toolchain verification

`nrniv` starts successfully. `nrnivmodl` compiled
`mechanisms/linear_leak.mod`, and Python loaded and inserted the resulting
`linearleak` mechanism. The registered Jupyter kernel independently imported
NEURON 9.0.2.

## Boundary

This proves local software integration and behavior of one illustrative cable
model. It does not identify a human neuron type, fit experimental recordings,
model learning or mental health, validate a drug mechanism, or establish
biological accuracy beyond the explicitly tested properties.
