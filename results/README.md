# Saved experiment index

This directory preserves the evidence behind the figures and written results.
The folders are outputs from local teaching experiments, not measured human or
animal data.

## Canonical examples

| Experiment | Directory | Contents |
|---|---|---|
| Original single neuron | repository-level `results/` files | Sweep table, voltage trace, checks, and figure |
| Circuit baseline | `circuit/20260906T032257Z-4791e73e/` | Twelve condition/seed runs, metrics, manifest, interpretation, and overview |
| Circuit finer step | `circuit/20260906T032858Z-16826dc0/` | Numerical comparison and verification receipt |
| Circuit no-pulse control | `circuit/20260906T033031Z-7e47e017/` | Negative-control arrays and metrics |
| Circuit size sensitivity | `size_sensitivity/20260906T140909Z-07b518e4/` | Three-size comparison, checks, tables, and figure |
| Ion channels | `multiscale/20260907T013217Z-ion_channels-6778e803/` | Four conditions, raw traces, checks, and figure |
| Reaction network | `multiscale/20260907T013232Z-reaction_network-df1ab0c1/` | Full/reduced calculations, model source, checks, and figure |
| Brain regions | `multiscale/20260907T013444Z-brain_regions-0b402927/` | Connectome arrays, regional traces, checks, and figure |
| NEURON compartments | `neuron_compartments/` | Soma/midpoint/tip voltage, numerical checks, and figure |
| Visual bridge | `visual_bridge/` | Anatomy-aware snapshots, animation, and source-run receipt |

Some circuit and regional folders preserve earlier or supporting runs. They are
kept because repeated, corrected, negative, and numerically compared runs are
part of the audit trail. The associated experiment reports identify which run
supports each claim.

## How a new experiment is saved

1. Write a question, prediction, primary measure, control, falsifier, and
   stopping rule.
2. Run a fixed protocol. Do not tune parameters after seeing the result merely
   to obtain a preferred figure.
3. Save raw arrays before plotting them.
4. Save enough configuration and environment information to trace the run.
5. Keep failed or null results and label incomplete manifests honestly.
6. Write the result and limitation together.

The generated path printed by `lessons/run.py`, `circuit_lab.py`, or
`size_sensitivity.py` is the permanent record for that run. New output should
use a new unique directory rather than replacing one of these examples.
