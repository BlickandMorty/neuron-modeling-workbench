# Ketamine, brain dynamics, and PTSD

## Evidence map for a mathematical learning project

**Scope:** research available through 5 September 2026; prepared for Jordan's local science workbench. This is a structured, selective evidence review, not an exhaustive systematic review or treatment advice. The executable model is a teaching circuit. No human data have been fitted to it.

### The central conclusion

Ketamine produces effects at several levels and time scales. There is no established equation connecting receptor blockade, a person's acute experience, plasticity, and PTSD recovery. A useful project makes those missing links visible and tests narrower claims. More mechanisms in a diagram do not automatically make a simulation more accurate.

The initial project question is deliberately specific: **how do assumed reductions in NMDA conductance on different cell populations change circuit activity?** It does not yet answer whether ketamine improves PTSD, erases a memory, or alters consciousness through a particular mechanism.

## 1 · Receptors and circuit dynamics

The [Wang-model implementation in Brian2](https://brian2.readthedocs.io/en/stable/examples/frompapers.Wang_2002.html) supplies a transparent mathematical starting point for recurrent AMPA, NMDA and GABA currents. Our reduced model changes its architecture and experimental task; see [the model card](MODEL.md).

[Susin and Destexhe (2023)](https://www.eneuro.org/content/10/11/ENEURO.0157-23.2023) investigated increased excitation and gamma activity following assumed differential NMDA antagonism. Their results also distinguish responsiveness to an input from ongoing excitability: these are not identical quantities. It is a model-based mechanism proposal, not a universal ketamine/PTSD response.

In [Rademacher et al. (2025)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1013118), healthy volunteers receiving S-ketamine showed gamma and aperiodic-spectrum changes. The authors' cell-type model captured some but not all observations. Their human MEG/clinical data are not publicly released, although [analysis/model code is public](https://github.com/jessierademacher/Ketamine_E-I). Our v1 does not recreate their MEG measurement process or infer PV/SST cell activity from a simple spectrum.

**Interpretation:** cell types, brain regions, task state and measurement method matter. A population-rate spectrum is a different observable from scalp EEG or MEG. Band power is not a direct consciousness or recovery score.

## 2 · BDNF and plasticity: pathways, not one settled chain

[Maeng et al. (2008)](https://pubmed.ncbi.nlm.nih.gov/17643398/) support a role for AMPA signaling in animal antidepressant-like effects. This does not imply direct AMPA agonism. [Autry et al. (2011)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3172695/) support an eEF2/BDNF mechanism involving resting NMDA blockade in mice and cultured neurons; this need not be identical to a circuit-disinhibition account.

[Li et al. (2010)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3116441/) connect ketamine with mTOR-related signaling and later synaptic changes in rats. However, a [small human rapamycin study](https://www.nature.com/articles/s41386-020-0644-9) did not reproduce the simple prediction that mTOR inhibition should abolish the early antidepressant response. Route and central target engagement prevent either experiment from settling the whole human mechanism.

[Moda-Sava et al. (2019)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6785189/) found an important temporal separation: some initial functional changes preceded new spine formation, while new spines contributed to maintaining certain later effects. [Casarotto et al. (2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7938888/) provide preclinical support for proposed direct TRKB interactions; clinical exposure and causal translation require further work.

**Implementation decision:** keep these pathways in the evidence library. No “BDNF level” slider is added without a defined compartment, measured quantity, governing dynamics and traceable parameterization. Blood biomarkers, brain protein levels and synaptic effects are not interchangeable measurements.

## 3 · Other mechanisms and exposure contexts

[HCN1 experiments](https://pubmed.ncbi.nlm.nih.gov/19158287/) concern hypnotic/anesthetic actions. They should not be transferred automatically to a low-exposure PTSD model.

[Zanos et al. (2016)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4922311/) motivate metabolite hypotheses. [HNK receptor experiments](https://pmc.ncbi.nlm.nih.gov/articles/PMC7406986/) show why “NMDA-independent” must be interpreted with concentration and assay context. A [human HNK phase 1 study](https://pmc.ncbi.nlm.nih.gov/articles/PMC11479831/) is relevant to future PK work, but is not proof of PTSD efficacy.

Human opioid-system interventions remain informative but contested. [Williams et al. (2018)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6395554/) and [Jelen et al. (2025)](https://pubmed.ncbi.nlm.nih.gov/40707608/) support involvement under their designs. A [different depression/alcohol-use-disorder trial](https://pmc.ncbi.nlm.nih.gov/articles/PMC12395335/) did not establish primary-outcome separation. These studies differ in populations, regimens and controls. Opioid involvement does not reduce ketamine to a single opioid mechanism; MRS metabolite ratios are not direct synaptic-release measurements.

[Adenosine work published in 2025](https://www.nature.com/articles/s41586-025-09755-9) adds an emerging preclinical hypothesis. It belongs in the map without being promoted to a settled human pathway.

## 4 · PTSD outcomes and acute effects

[Feder et al. (2014)](https://jamanetwork.com/journals/jamapsychiatry/fullarticle/1860851) and [Feder et al. (2021)](https://pubmed.ncbi.nlm.nih.gov/33397139/) provide positive findings from small controlled PTSD studies, including improvement beyond the immediate acute state.

The [larger 2022 military/veteran trial](https://www.nature.com/articles/s41386-022-01266-9) did not find significant superiority on PTSD outcomes, despite clear transient dissociative effects. Acute dissociation also became less pronounced over repeated administration. A [newer intramuscular crossover study](https://pubmed.ncbi.nlm.nih.gov/41030011/) reported preliminary positive results, but its route, comparator and sample differ.

The [VA guide describing the 2023 VA/DoD guideline](https://www.ptsd.va.gov/professional/treat/txessentials/clinician_guide_meds.asp) suggests against ketamine for PTSD monotherapy. This guideline predates newer studies and is not interchangeable with depression indications.

**What “acute is more pronounced” can mean:** large acute changes on a particular physiological or experiential measure. It cannot by itself mean those changes produce more therapeutic benefit, or are stronger in PTSD than healthy participants. A diagnosis-by-intervention interaction requires a suitable direct comparison. The evidence reviewed does not supply a universal PTSD amplification coefficient.

## 5 · Automatic responses, cognition and threat learning

Your idea can become a research question about conditioned response strength, safety learning, generalization, recovery, or return of responding. It should not begin with a built-in “pattern reset” variable.

A controlled [human memory-reactivation study](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0065088) found stronger subsequent fear-memory expression after reactivation under ketamine. That is a useful counterexample to automatic memory weakening, not proof of what happens in PTSD treatment.

The [acute PTSD connectivity pilot](https://link.springer.com/article/10.1007/s00213-023-06479-4) did not support its preregistered increase in the targeted connectivity measure. A related [retrieval-plus-exposure-therapy paper](https://www.nature.com/articles/s41386-023-01606-3) found neural differences despite similar symptom improvement. They share an underlying trial and must not be counted as independent replications.

An [uncontrolled cognition study including MDD/PTSD and healthy participants](https://www.nature.com/articles/s41398-021-01327-5) reported transient changes in some cognitive domains. Absence of placebo and randomization limits causal interpretation. Cognition is not one scalar: attention, memory encoding, retrieval and executive tasks may behave differently.

## 6 · Autonomic effects and harms

A [randomized healthy-volunteer study](https://pubmed.ncbi.nlm.nih.gov/29099972/) documented acute cardiovascular increases. Therefore an eventual autonomic component cannot assume uniform physiological calming.

This release records acute dissociation, cognitive and cardiovascular observations, and repeated-infusion attenuation. **Chronic high-frequency exposure, dependence, long-term cognitive effects, urinary toxicity, sleep, endocrine and inflammatory effects have not received full primary-source adjudication here.** They remain explicit gaps, not assumed absent effects. Anesthetic, repeated clinical and chronic nonmedical exposures must stay separate.

## What you can claim from this release

- You have an AI-assisted, reproducible teaching circuit and a source-linked evidence map.
- You can state which assumptions changed and what numerical outputs followed.
- You cannot infer individual treatment response, a real PTSD brain state, or the truth of a molecular mechanism from these runs.

The next research milestone is an exact reference-model replication with its original observable, then a narrowly chosen external-data comparison. The next learning milestone is your own explained prediction, derivation and controlled modification—not a larger list of mechanisms.

## Access and search limitations

The companion [evidence table](evidence.json) holds source, population, route, timing, uncertainty and cohort information. Several primary records were accessible only through abstracts/indexed results; those are marked. No risk-of-bias meta-analysis or exhaustive database export was completed. The [search audit](SEARCH_AUDIT.md) records the passes and unresolved gaps. No inaccessible individual data were fabricated or reconstructed as observations.
