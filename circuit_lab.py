"""Source-linked teaching circuit, NOT a calibrated ketamine/PTSD model.

Equations and conductance scales follow the Brian2 Wang (2002) example.
Independent reduced implementation: no selective decision pools or clinical fit.
See research/MODEL.md for every departure and measurement definition.
"""
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import platform
import uuid

import brian2 as b
import numpy as np
import pandas as pd
from scipy.signal import welch

ROOT = Path(__file__).resolve().parent
MODEL_VERSION = "teaching-ei-0.1.0"
SOURCE = "https://brian2.readthedocs.io/en/2.10.1/examples/frompapers.Wang_2002.html"
BOUNDARY = "Synthetic circuit; no human recordings, clinical dose, PTSD diagnosis, or treatment prediction."
VARIANTS = {"recurrent_excitation": "excitation_scale", "inhibition": "inhibition_scale", "external_input": "external_scale"}


@dataclass(frozen=True)
class Config:
    n_e: int = 80
    n_i: int = 20
    duration_ms: float = 2000.0
    dt_ms: float = 0.1
    record_ms: float = 1.0
    seed: int = 11
    block_e: float = 0.0
    block_i: float = 0.0
    excitation_scale: float = 1.0
    inhibition_scale: float = 1.0
    external_scale: float = 1.0
    stimulus_pa: float = 150.0
    stimulus_on_ms: float = 800.0
    stimulus_off_ms: float = 900.0

    def validate(self):
        for key, value in asdict(self).items():
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not np.isfinite(value):
                raise ValueError(f"{key} must be a finite number")
        if any(not isinstance(v, int) for v in [self.n_e, self.n_i, self.seed]):
            raise ValueError("Population sizes and seed must be integers")
        if not (2 <= self.n_e <= 400 and 2 <= self.n_i <= 100 and 0 <= self.seed < 2**32):
            raise ValueError("Teaching limits: E 2..400, I 2..100; seed 0..2**32-1")
        if not (0 <= self.block_e <= 1 and 0 <= self.block_i <= 1):
            raise ValueError("NMDA reduction fractions must lie in [0, 1], not clinical dose units")
        if not all(0 <= v <= 2 for v in [self.excitation_scale, self.inhibition_scale, self.external_scale]):
            raise ValueError("Circuit scale factors must lie in [0, 2]")
        if not (0.025 <= self.dt_ms <= 0.1 and 0.5 <= self.record_ms <= 2):
            raise ValueError("dt must be 0.025..0.1 ms; recording interval 0.5..2 ms")
        if not (100 <= self.duration_ms <= 10000 and 0 <= self.stimulus_pa <= 500):
            raise ValueError("Duration must be 100..10000 ms; pulse 0..500 pA")
        if not (0 <= self.stimulus_on_ms < self.stimulus_off_ms < self.duration_ms):
            raise ValueError("Pulse times must be ordered and inside the simulation")
        for interval in [self.record_ms, self.duration_ms, self.stimulus_on_ms, self.stimulus_off_ms, 0.5]:
            if not np.isclose(interval / self.dt_ms, round(interval / self.dt_ms)):
                raise ValueError("Timing intervals must be integer multiples of dt")


def nmda_voltage_factor(voltage_mv):
    """Dimensionless magnesium-block factor at the reference 1 mM Mg concentration."""
    return 1.0 / (1.0 + np.exp(-0.062 * np.asarray(voltage_mv)) / 3.57)


def simulate(config=Config()):
    config.validate()
    b.prefs.codegen.target = "numpy"  # portable Windows CPU backend; no compiler needed
    b.start_scope()
    b.seed(config.seed)
    clock = b.Clock(dt=config.dt_ms * b.ms)
    equations = """
    dv/dt = (-g_leak*(v-EL)-I_AMPA-I_NMDA-I_GABA-I_external+I_pulse)/cap : volt (unless refractory)
    I_AMPA = ga*(v-EE) : amp
    I_GABA = gg*(v-EI) : amp
    I_NMDA = gn*nmda_total*(v-EE)/(1+exp(-0.062*v/mV)/3.57) : amp
    I_external = gx*(v-EE) : amp
    I_pulse = pulse*int(t>=pulse_on)*int(t<pulse_off) : amp
    dga/dt = -ga/(2*ms) : siemens
    dgg/dt = -gg/(5*ms) : siemens
    dgx/dt = -gx/(2*ms) : siemens
    ds/dt = -s/(100*ms) + 0.5/ms*x*(1-s) : 1
    dx/dt = -x/(2*ms) : 1
    nmda_total : 1
    gn : siemens (constant)
    cap : farad (constant)
    g_leak : siemens (constant)
    pulse : amp (constant)
    ref : second (constant)
    """
    namespace = {"EL": -70*b.mV, "EE": 0*b.mV, "EI": -70*b.mV,
                 "pulse_on": config.stimulus_on_ms*b.ms, "pulse_off": config.stimulus_off_ms*b.ms}
    groups = []
    for n, cap, leak, ref, gn, pulse in [
        (config.n_e, 500, 25, 2, 0.165*(1-config.block_e), config.stimulus_pa),
        (config.n_i, 200, 20, 1, 0.13*(1-config.block_i), 0),
    ]:
        g = b.NeuronGroup(n, equations, threshold="v>=-50*mV", reset="v=-55*mV",
                          refractory="ref", method="euler", clock=clock, namespace=namespace)
        g.cap = cap*b.pF
        g.g_leak = leak*b.nS
        g.ref = ref*b.ms
        g.gn = gn * (1600/config.n_e) * config.excitation_scale * b.nS
        g.pulse = pulse*b.pA
        g.v = "-70*mV + rand()*10*mV"
        groups.append(g)
    exc, inh = groups
    objects = list(groups)
    # All-to-all coupling permits summing presynaptic NMDA gates once.
    # This is NOT valid unchanged for heterogeneous synaptic delays/kinetics.
    gate_events = b.Synapses(exc, exc, on_pre="x_post += 1", delay=0.5*b.ms, clock=clock)
    gate_events.connect(j="i")
    total = b.NeuronGroup(1, "s_total : 1", clock=clock)
    summer = b.Synapses(exc, total, "s_total_post = s_pre : 1 (summed)", clock=clock)
    summer.connect()
    objects.extend([gate_events, total, summer])
    for g in groups:
        broadcast = b.Synapses(total, g, "nmda_total_post = s_total_pre : 1 (summed)", clock=clock)
        broadcast.connect()
        objects.append(broadcast)
    for pre, post, variable, weight in [
        (exc, exc, "ga", .05*1600/config.n_e*config.excitation_scale),
        (exc, inh, "ga", .04*1600/config.n_e*config.excitation_scale),
        (inh, exc, "gg", 1.3*400/config.n_i*config.inhibition_scale),
        (inh, inh, "gg", 1.0*400/config.n_i*config.inhibition_scale),
    ]:
        syn = b.Synapses(pre, post, "weight : siemens (constant)",
                         on_pre=f"{variable}_post += weight", delay=.5*b.ms, clock=clock)
        syn.connect()  # includes autapses, matching homogeneous reference connectivity
        syn.weight = weight*b.nS
        objects.append(syn)
    for g, weight in [(exc, 2.1), (inh, 1.62)]:
        objects.append(b.PoissonInput(g, "gx", 1000, 2.4*config.external_scale*b.Hz, weight*b.nS))
    spikes = [b.SpikeMonitor(g) for g in groups]
    traces = [b.StateMonitor(g, ["v", "I_AMPA", "I_NMDA", "I_GABA", "I_external", "s"],
                            record=[0], dt=config.record_ms*b.ms) for g in groups]
    objects.extend(spikes + traces)
    b.Network(objects).run(config.duration_ms*b.ms, namespace={})
    result = {"config": asdict(config), "t_ms": np.asarray(traces[0].t/b.ms)}
    for label, sm, tm in zip(["e", "i"], spikes, traces):
        result[f"spike_t_{label}"] = np.asarray(sm.t/b.ms)
        result[f"spike_id_{label}"] = np.asarray(sm.i)
        result[f"v_{label}"] = np.asarray(tm.v[0]/b.mV)
        for field in ["I_AMPA", "I_NMDA", "I_GABA", "I_external"]:
            result[f"{field}_{label}"] = np.asarray(getattr(tm, field)[0]/b.pA)
        result[f"gate_{label}"] = np.asarray(tm.s[0])
    if not all(np.all(np.isfinite(v)) for v in result.values() if isinstance(v, np.ndarray)):
        raise FloatingPointError("Nonfinite simulated state: do not interpret this run")
    return result


def firing_trace(result, label="e", bin_ms=5.):
    c = result["config"]
    edges = np.arange(0, c["duration_ms"] + 1e-8, bin_ms)
    counts, _ = np.histogram(result[f"spike_t_{label}"], edges)
    return (edges[:-1]+edges[1:])/2, counts/(c[f"n_{label}"]*bin_ms/1000)


def spectrum(result, label="e"):
    """Welch PSD of 1-ms population spike-count rates, not EEG or LFP."""
    t, rate = firing_trace(result, label, 1.)
    keep = t >= result["config"]["stimulus_off_ms"] + 200
    if keep.sum() < 256:
        return np.array([]), np.array([])
    return welch(rate[keep], fs=1000., window="hann", nperseg=256, noverlap=128, detrend="constant")


def metrics(result):
    c = result["config"]
    output = {}
    windows = {"pre": (max(0, c["stimulus_on_ms"]-300), c["stimulus_on_ms"]),
               "pulse": (c["stimulus_on_ms"], c["stimulus_off_ms"]),
               "post": (c["stimulus_off_ms"]+200, c["duration_ms"])}
    for label in ["e", "i"]:
        spikes = result[f"spike_t_{label}"]
        for window, (start, end) in windows.items():
            output[f"{label}_{window}_hz"] = (float(np.sum((spikes >= start) & (spikes < end))) /
                                              ((end-start)/1000*c[f"n_{label}"])) if end > start else None
        output[f"{label}_pulse_minus_pre_hz"] = output[f"{label}_pulse_hz"]-output[f"{label}_pre_hz"]
        f, p = spectrum(result, label)
        band = (f >= 30) & (f <= 90)
        output[f"{label}_30_90_power_hz2"] = float(np.trapezoid(p[band], f[band])) if band.sum() > 1 else None
    return output


def conditions(base, variant="inhibition", variant_scale=.85):
    if variant not in VARIANTS:
        raise ValueError(f"Unknown variant: {variant}")
    if not np.isfinite(variant_scale) or not 0 <= variant_scale <= 2:
        raise ValueError("Variant scale must lie in [0, 2]")
    # Reference always has unmodified circuit factors. Only ONE factor changes in a variant.
    clean = replace(base, excitation_scale=1., inhibition_scale=1., external_scale=1.)
    altered = replace(clean, **{VARIANTS[variant]: variant_scale})
    return {"reference_control": replace(clean, block_e=0., block_i=0.),
            "reference_perturbed": clean,
            "variant_control": replace(altered, block_e=0., block_i=0.),
            "variant_perturbed": altered}


def run_comparison(base=None, seeds=(11, 22, 33), variant="inhibition", variant_scale=.85,
                   prediction="Not recorded", output_root=None, progress=None):
    base = base or Config(block_e=.1, block_i=.3)
    seeds = tuple(seeds)
    if not seeds or len(seeds) != len(set(seeds)):
        raise ValueError("Use at least one distinct seed")
    cases = conditions(base, variant, variant_scale)
    for c in cases.values():
        for seed in seeds:
            replace(c, seed=seed).validate()
    root = Path(output_root) if output_root else ROOT/"results"/"circuit"
    run_dir = root/(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"-"+uuid.uuid4().hex[:8])
    run_dir.mkdir(parents=True, exist_ok=False)
    manifest = {"model_version": MODEL_VERSION, "source_url": SOURCE,
                "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "environment": {"python": platform.python_version(), "brian2": b.__version__, "numpy": np.__version__},
                "data_origin": "simulation", "boundary": BOUNDARY,
                "prediction": prediction, "interpretation": "Not yet written by learner",
                "variant": variant, "variant_scale": variant_scale, "seeds": seeds,
                "configurations": {key: asdict(val) for key, val in cases.items()}, "status": "running"}
    (run_dir/"manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    rows, results = [], {}
    try:
        for name, c in cases.items():
            for seed in seeds:
                if progress:
                    progress(f"{name}, seed {seed} ({len(rows)+1}/{len(cases)*len(seeds)})")
                result = simulate(replace(c, seed=seed))
                payload = {k: v for k, v in result.items() if k != "config"}
                payload["config_json"] = json.dumps(result["config"])
                np.savez_compressed(run_dir/f"{name}_seed{seed}.npz", **payload)
                row = {"condition": name, "seed": seed, **metrics(result)}
                rows.append(row)
                if seed == seeds[0]:
                    results[name] = result
        table = pd.DataFrame(rows)
        table.to_csv(run_dir/"metrics.csv", index=False)
        manifest["status"] = "complete"
        manifest["checks"] = {"finite_outputs": True, "clinical_validation": False}
        manifest["artifacts_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                        for p in run_dir.iterdir() if p.suffix in [".npz", ".csv"]}
        (run_dir/"interpretation.md").write_text(
            "# Interpret this experiment\n\nQuestion: How do cell-targeted NMDA reductions change circuit activity?\n\n"
            f"Prediction before running: {prediction}\n\n"
            "Method: four matched synthetic conditions; identical seeds within comparisons.\n\n"
            "Result: inspect metrics.csv and the saved traces.\n\n"
            "Your explanation: [write what changed, what did not, and an alternative explanation]\n\n"
            "Falsifier: a zero/opposite response weakens the proposed directional circuit hypothesis.\n\n"
            "Stopping rule: finish this fixed seed set; do not tune away null results.\n\n"
            f"Boundary: {BOUNDARY}\n", encoding="utf-8")
    except Exception as exc:
        manifest["status"] = "failed"
        manifest["error"] = repr(exc)
        raise
    finally:
        (run_dir/"manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return table, results, run_dir


def load_run(run_dir):
    run_dir = Path(run_dir)
    manifest = json.loads((run_dir/"manifest.json").read_text(encoding="utf-8"))
    if manifest["status"] != "complete":
        raise ValueError("Run is incomplete; inspect its manifest before interpreting")
    for name, expected in manifest["artifacts_sha256"].items():
        if hashlib.sha256((run_dir/name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Artifact changed since run: {name}")
    results = {}
    for name in manifest["configurations"]:
        with np.load(run_dir/f"{name}_seed{manifest['seeds'][0]}.npz", allow_pickle=False) as data:
            results[name] = {k: data[k] for k in data.files if k != "config_json"}
            results[name]["config"] = json.loads(str(data["config_json"]))
    return pd.read_csv(run_dir/"metrics.csv"), results, run_dir


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, nargs="+", default=[11, 22, 33])
    parser.add_argument("--dt", type=float, default=.1)
    parser.add_argument("--variant", choices=VARIANTS, default="inhibition")
    parser.add_argument("--scale", type=float, default=.85)
    parser.add_argument("--block-e", type=float, default=.1)
    parser.add_argument("--block-i", type=float, default=.3)
    args = parser.parse_args()
    table, _, folder = run_comparison(Config(dt_ms=args.dt, block_e=args.block_e, block_i=args.block_i),
                                      seeds=args.seeds, variant=args.variant, variant_scale=args.scale,
                                      progress=lambda s: print(s, flush=True))
    print(table.to_string(index=False))
    print(folder)
