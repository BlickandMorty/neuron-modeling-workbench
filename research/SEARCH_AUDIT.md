# Research audit and remaining gaps

Scope cutoff: 2026-09-05. This is a v1 selective evidence map supporting a teaching model, not a completed systematic review of every reported ketamine effect. Publication records and observed source text were inspected through web retrieval; no participant data were obtained.

## Pass 1: foundational discovery (planning)

Question families: ketamine acute brain rhythms and NMDA circuit models; PTSD controlled trials; BDNF/eEF2/mTOR/TrkB; metabolites, HCN and opioid-system interventions. Primary sources and official documentation were prioritized. Searches included `ketamine acute human EEG gamma alpha computational model NMDA interneurons open source`, `ketamine PTSD randomized trial`, and mechanism-specific primary-paper searches.

Result: distinguish human observations, preclinical causal manipulations, model assumptions and clinical efficacy. The Brian2 example supplies executable equation provenance; the 2023 and 2025 models supply comparison targets, not validated parameters for PTSD.

## Pass 2: contradictions and translation (planning + implementation)

Queries targeted the 158-person negative trial, rapamycin human translation, naltrexone results and conflicting samples, HNK receptor findings, acute versus persistent spine effects, and PTSD connectivity. Additional implementation-pass queries:

- `ketamine fear extinction reconsolidation human randomized 2023 2024 primary study`
- `ketamine PTSD acute memory cognition randomized placebo healthy volunteers attention study`
- `ketamine human autonomic blood pressure heart rate Liebe 2017 68`

Result: preserve positive and negative PTSD trials; do not treat acute dissociation as efficacy. Added Corlett 2013 as a direct contrary memory result, and flagged lack of placebo/randomization in the cognition comparison. Danbock and Duek share a cohort identifier; their differing analyzed sample sizes do not make them independent studies.

## Pass 3: parameters, access and implementation feasibility

Read the official Brian2 Wang2002 example and extracted membrane/synapse constants into MODEL.md. Read Susin2023 methods through Europe PMC XML: it uses an AdEx architecture distinct from our LIF teaching circuit. The methods/figure descriptions contain details requiring reconciliation before exact replication; these were not silently imported.

Read the Rademacher2025 publisher results and data-availability statement, and the linked GitHub README. Analysis code is public; human MEG/clinical data are not released publicly. An open repository is not automatically a reusable-license grant; license and dependencies must be checked before vendoring code. We wrote the reduced teaching implementation independently from referenced equations rather than copying that repository.

No human concentration-to-conductance mapping was established. No exposure units are shown on circuit perturbation controls. No whole-brain or EEG forward model is implemented.

## Gap matrix and stopping rule

| Claim or capability | Current boundary | Next targeted action |
|---|---|---|
| Universal PTSD amplification | No adequate quantitative interaction established | Locate directly comparable diagnosis-by-drug recordings and model heterogeneity |
| Automatic learned-pattern weakening | Counterexamples and mixed contexts | Define one task/endpoint; extract retrieval, extinction, timing and control conditions |
| BDNF/plasticity dynamics | Predominantly preclinical mechanisms; no human coefficients | Select compartment and observable before fitting a slow module |
| Human dose slider | No validated PK/PD bridge | Extract formulation-specific PK, unbound exposure and receptor-effect uncertainty |
| Real EEG/MEG calibration | Candidate study data restricted | Find open licensed recordings with intervention metadata; do not substitute unrelated EEG as ketamine data |
| Chronic exposure/adverse effects | Incomplete primary adjudication | Dedicated exposure-stratified review of cognitive, dependence and organ toxicity outcomes |
| Exact published replication | Teaching adaptation only | Pin source/version, reconcile parameters and match measurement pipeline |
| New primary studies | Recent records selectively checked | Repeat dated searches before making clinical summaries or adding mechanisms |

Stopping reason for v1: the implemented circuit question has a source-linked mathematical specification, the major causal translation errors are bounded, and unsupported mechanisms are excluded from executable claims. Further broad literature collection would not validate this toy circuit. Missing families remain visible and should be addressed in targeted future modules.

## Provenance files

### Model-scale follow-up, 2026-09-06

Checked the official Brian2 example's 2,000-cell count and Rademacher2025 methods (1,000-cell layer-2/3 microcircuit, NEURON/LFPy, restricted human recordings). Searched `The Virtual Brain 2013 neuroinformatics platform full brain network simulations connectome neural mass Sanz Leon`; the primary 2013 platform paper supports the distinction between region/population models and individual-cell models. Direct TVB documentation opens failed in the browser research tool, so the source-linked research path uses the primary paper and does not claim a verified TVB installation. This follow-up informs model selection, not new ketamine efficacy evidence.

The size-sensitivity experiment tests a numerical/model-design assumption locally. It is not an expansion of the human evidence cohort or a paper replication.

`evidence.json` is the claim-to-source ledger and searchable notebook data source. `REPORT.md` is the readable synthesis. `MODEL.md` maps executable assumptions to their origin. Source access descriptions distinguish full inspected sections from abstract/indexed-only evidence. No inferred sample-level measurements have been stored as real observations.
