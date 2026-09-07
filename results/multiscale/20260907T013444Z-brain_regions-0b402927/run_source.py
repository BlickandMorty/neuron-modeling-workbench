"""Three independent, local teaching experiments. No patient or drug predictions.

Run with the matching environment documented in research/TOOLS_AND_LESSONS.md.
AI-assisted implementation; ownership exercises are in the notebooks and guide.
"""
import argparse
import csv
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import platform
import sys
from datetime import datetime, timezone
from uuid import uuid4

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
USER_PREDICTION = ""  # Set in the notebook before a new run, or use --prediction.


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def csv_table(path, columns, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)


def new_run(name, protocol):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "results" / "multiscale" / (stamp + "-" + name + "-" + uuid4().hex[:8])
    out.mkdir(parents=True)
    # This protocol is written before this run. These are tutorial expectations,
    # not an externally registered study or a blind prediction by Jordan.
    save_json(out / "manifest.json", {
        "created_utc": stamp, "lesson": name, "protocol": protocol,
        "python": sys.version, "executable": sys.executable,
        "platform": platform.platform(), "argv": sys.argv,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "packages": {d.metadata["Name"]: d.version for d in metadata.distributions()},
        "status": "started", "data_type": "simulation", "public": False,
        "user_prediction_before_run": USER_PREDICTION,
        "assistance": "AI implemented and ran the initial tutorial. Jordan's independent exercises are separate."
    })
    # Preserve the exact implementation even if the working file changes later.
    (out / "run_source.py").write_bytes(Path(__file__).read_bytes())
    return out


def finish(out, metrics, checks):
    save_json(out / "metrics.json", metrics)
    save_json(out / "checks.json", checks)
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    manifest["status"] = "passed" if all(checks.values()) else "check_failed"
    save_json(out / "manifest.json", manifest)
    (out / "MY_INTERPRETATION.md").write_text(
        "# My interpretation\n\nPrediction I wrote before my run:\n\n"
        "What I changed myself:\n\nWhat the measurements show:\n\n"
        "What surprised me or failed:\n\nWhat this cannot tell me:\n\n", encoding="utf-8")
    print(json.dumps({"output": str(out), "metrics": metrics, "checks": checks}, indent=2))
    if not all(checks.values()):
        raise RuntimeError("A verification check failed; preserve this run and investigate.")
    return out


def hh_rates(v):
    """Classical HH rates at 6.3 C; v is mV relative to outside, rest about -65.

    The removable singularities at -40 and -55 mV use their analytic limits.
    """
    def quotient(x):
        return 1 - x / 2 + x*x / 12 if abs(x) < 1e-7 else x / np.expm1(x)
    am = quotient(-(v + 40) / 10)
    bm = 4 * np.exp(-(v + 65) / 18)
    ah = .07 * np.exp(-(v + 65) / 20)
    bh = 1 / (1 + np.exp(-(v + 35) / 10))
    an = .1 * quotient(-(v + 55) / 10)
    bn = .125 * np.exp(-(v + 65) / 80)
    return np.array([am, ah, an]), np.array([bm, bh, bn])


def hh_trace(current=10., sodium_scale=1., max_step=.025):
    from scipy.integrate import solve_ivp
    a, b = hh_rates(-65.)
    state = np.r_[-65., a / (a + b)]
    times, states = [], []
    # Solve separately at pulse boundaries so an adaptive solver cannot skip an
    # abrupt input. Output spacing stays .025 ms in the finer-solver comparison.
    for start, stop, applied in [(0., 10., 0.), (10., 60., current), (60., 100., 0.)]:
        def rhs(t, y):
            v, m, hgate, n = y
            ina = 120 * sodium_scale * m**3 * hgate * (v - 50)
            ik = 36 * n**4 * (v + 77)
            leak = .3 * (v + 54.387)
            alpha, beta = hh_rates(v)
            gates = alpha * (1-y[1:]) - beta * y[1:]
            return np.r_[applied - ina - ik - leak, gates]  # Cm=1 uF/cm2
        grid = np.linspace(start, stop, round((stop-start)/.025)+1)
        sol = solve_ivp(rhs, (start, stop), state, t_eval=grid,
                        method="DOP853", rtol=1e-8, atol=1e-10, max_step=max_step)
        if not sol.success:
            raise RuntimeError(sol.message)
        state = sol.y[:, -1]
        offset = 0 if not times else 1
        times.extend(sol.t[offset:])
        states.extend(sol.y[:, offset:].T)
    t, y = np.array(times), np.array(states)
    v, m, hgate, n = y.T
    currents = np.column_stack((120*sodium_scale*m**3*hgate*(v-50),
                                 36*n**4*(v+77), .3*(v+54.387)))
    # Discrete upcrossings; resolution of the spike times is .025 ms.
    spikes = t[1:][(v[:-1] < 0) & (v[1:] >= 0)]
    return t, y, currents, spikes


def hh_lesson():
    protocol = {
        "question": "Which parts of an electrical spike depend on voltage-gated sodium conductance?",
        "prediction": "The 10 uA/cm2 baseline pulses; removing sodium conductance removes regenerative spikes.",
        "model": "Single isopotential classical Hodgkin-Huxley membrane, squid-axon-derived rates at 6.3 C",
        "parameters": {"gNa_mS_cm2":120, "gK_mS_cm2":36, "gL_mS_cm2":.3,
                       "ENa_mV":50, "EK_mV":-77, "EL_mV":-54.387, "Cm_uF_cm2":1},
        "conditions": [["no_input",0,1],["baseline",10,1],["half_sodium",10,.5],["no_sodium",10,0]],
        "pulse_ms":[10,60], "duration_ms":100, "primary_metric":"number of 0-mV upcrossings",
        "checks":"finite arrays, gate bounds, no-input/no-sodium controls, baseline spikes, finer solver <0.1mV discrepancy",
        "stop":"Run four conditions and one finer-step baseline once; keep unexpected results.",
        "boundary":"Not a human cell, cell morphology, ketamine pharmacology, or PTSD model."
    }
    out = new_run("ion_channels", protocol)
    records, traces = {}, {}
    for name, current, scale in protocol["conditions"]:
        t,y,currents,spikes = hh_trace(current,scale)
        traces[name]=(t,y,currents,spikes)
        csv_table(out / (name+".csv"),
                  ["time_ms","voltage_mV","m","h","n","INa_uA_cm2","IK_uA_cm2","IL_uA_cm2"],
                  np.column_stack((t,y,currents)))
        records[name]={"spikes":len(spikes),"spike_times_ms":spikes.tolist(),
                       "peak_mV":float(y[:,0].max())}
    t,y,currents,spikes=traces["baseline"]
    tf,yf,cf,sf=hh_trace(max_step=.0125)
    csv_table(out/"baseline_finer.csv",["time_ms","voltage_mV","m","h","n"],np.column_stack((tf,yf)))
    error=float(np.max(np.abs(y[:,0]-yf[:,0])))
    records["solver_max_voltage_difference_mV"]=error
    fig,axes=plt.subplots(3,1,figsize=(10,9),sharex=True,layout="constrained")
    for name,(ti,yi,_,_) in traces.items():
        axes[0].plot(ti,yi[:,0],label=name.replace("_"," "))
    axes[0].set_ylabel("Membrane voltage (mV)")
    axes[0].legend(ncol=2)
    for index,label in enumerate(["Na inward (negative)","K outward (positive)","leak"]):
        axes[1].plot(t,currents[:,index],label=label)
    axes[1].set_ylabel("Baseline current (uA/cm2)")
    axes[1].legend()
    for index,label in enumerate(["m: Na activation","h: Na availability","n: K activation"],1):
        axes[2].plot(t,y[:,index],label=label)
    axes[2].set(xlabel="Time (ms)",ylabel="Gate variable (0 to 1)",ylim=(-.03,1.03))
    axes[2].legend()
    for ax in axes:
        ax.axvspan(10,60,color="grey",alpha=.08)
        ax.grid(alpha=.15)
    fig.suptitle("Ion-channel teaching model — simulated, not a human recording")
    fig.savefig(out/"ion_channels.png",dpi=150)
    plt.close(fig)
    checks={"finite":all(np.isfinite(v[1]).all() for v in traces.values()),
            "gates_bounded":all(((v[1][:,1:]>=-1e-8)&(v[1][:,1:]<=1+1e-8)).all().item() for v in traces.values()),
            "no_input_silent":records["no_input"]["spikes"]==0,
            "no_sodium_silent":records["no_sodium"]["spikes"]==0,
            "baseline_spikes":records["baseline"]["spikes"]>0,
            "finer_solver_voltage":error<.1,
            "finer_solver_spike_count":len(spikes)==len(sf)}
    return finish(out,records,checks)


def reaction_lesson():
    import tellurium as te
    from scipy.integrate import solve_ivp
    protocol={
        "question":"When does a reduced enzyme-rate equation differ from the explicit binding model?",
        "prediction":"Conserved totals remain constant; increasing enzyme relative to substrate can worsen the reduction.",
        "reactions":"E+S <-> ES -> E+P", "parameters":{"k1_uM_inv_s_inv":.01,"km1_s_inv":.1,"kcat_s_inv":.2,"S0_uM":100},
        "enzyme_totals_uM":[1,20], "duration_s":100,
        "primary_metric":"maximum absolute product difference in uM versus Michaelis-Menten approximation",
        "checks":"mass conservation <1e-5uM, nonnegativity >=-1e-8uM, independent SciPy solution agreement <1e-3uM",
        "stop":"Two enzyme amounts, unchanged rate constants; keep either direction of discrepancy.",
        "boundary":"Generic invented enzyme example, not BDNF, mTOR, ketamine, or measured kinetic constants."
    }
    out=new_run("reaction_network",protocol)
    metrics,checks={},{}
    fig,axes=plt.subplots(2,2,figsize=(11,7),layout="constrained")
    model="""model enzyme()
      compartment cell=1;
      species E in cell, S in cell, ES in cell, P in cell;
      J1: E + S -> ES; k1*E*S;
      J2: ES -> E + S; km1*ES;
      J3: ES -> E + P; kcat*ES;
      E=1; S=100; ES=0; P=0;
      k1=0.01; km1=0.1; kcat=0.2;
    end"""
    (out/"model.ant").write_text(model,encoding="utf-8")
    for row,enzyme in enumerate([1,20]):
        r=te.loada(model)
        r.E=enzyme
        r.integrator.relative_tolerance=1e-9
        r.integrator.absolute_tolerance=1e-11
        full=np.asarray(r.simulate(0,100,1001,selections=["time","[E]","[S]","[ES]","[P]"]))
        t=full[:,0]
        def full_rhs(t,y):
            e,s,es,p=y
            binding=.01*e*s
            unbinding=.1*es
            conversion=.2*es
            return [-binding+unbinding+conversion,-binding+unbinding,binding-unbinding-conversion,conversion]
        independent=solve_ivp(full_rhs,(0,100),[enzyme,100,0,0],t_eval=t,rtol=1e-9,atol=1e-11,method="LSODA")
        if not independent.success:
            raise RuntimeError(independent.message)
        reduced=solve_ivp(lambda t,s:[-.2*enzyme*s[0]/(30+s[0])],(0,100),[100.],t_eval=t,rtol=1e-10,atol=1e-12)
        if not reduced.success:
            raise RuntimeError(reduced.message)
        p_reduced=100-reduced.y[0]
        err=float(np.max(np.abs(full[:,4]-p_reduced)))
        conserved=max(float(np.max(np.abs(full[:,1]+full[:,3]-enzyme))),
                      float(np.max(np.abs(full[:,2]+full[:,3]+full[:,4]-100))))
        solver_error=float(np.max(np.abs(full[:,1:]-independent.y.T)))
        metrics[str(enzyme)]={"max_product_approximation_error_uM":err,
                             "max_conservation_error_uM":conserved,
                             "max_independent_solver_error_uM":solver_error,
                             "final_product_uM":float(full[-1,4])}
        checks[str(enzyme)+"_conservation"]=conserved<1e-5
        checks[str(enzyme)+"_nonnegative"]=bool(full[:,1:].min()>=-1e-8)
        checks[str(enzyme)+"_independent_solver"]=solver_error<1e-3
        csv_table(out/f"enzyme_{enzyme}.csv",["time_s","E_uM","S_uM","ES_uM","P_uM","P_reduced_uM"],np.column_stack((full,p_reduced)))
        for index,label in [(2,"free substrate"),(3,"bound complex"),(4,"product")]:
            axes[row,0].plot(t,full[:,index],label=label)
        axes[row,0].set(title=f"Enzyme total = {enzyme} uM",xlabel="Time (s)",ylabel="Concentration (uM)")
        axes[row,0].legend()
        axes[row,1].plot(t,full[:,4],label="explicit binding")
        axes[row,1].plot(t,p_reduced,"--",label="reduced rate equation")
        axes[row,1].set(xlabel="Time (s)",ylabel="Product (uM)",title=f"Maximum discrepancy: {err:.3f} uM")
        axes[row,1].legend()
    fig.suptitle("A biochemical modeling lesson — illustrative parameters, simulated data")
    fig.savefig(out/"reaction_network.png",dpi=150)
    plt.close(fig)
    return finish(out,metrics,checks)


def region_lesson():
    from tvb.simulator.lab import connectivity, models, coupling, integrators, monitors, simulator
    protocol={
        "question":"What changes when regional oscillators communicate through a connectome?",
        "prediction":"Coupling can change trajectories; a synchrony increase is not guaranteed.",
        "model":"TVB Generic2dOscillator, a=2 (oscillatory example), other defaults exported",
        "connectivity":"tvb-data bundled connectivity_76.zip; weights divided by maximum row sum",
        "couplings":[0,.02], "dt_ms":.1,"finer_dt_ms":.05,"duration_ms":500,
        "speed_mm_per_ms":3,"initial_state_seed":42,"transient_discard_ms":100,
        "primary_metric":"RMS difference in region V trajectories, same initial history",
        "checks":"finite values, deterministic repeat agreement <1e-12, finer-step RMS discrepancy <0.05 model units",
        "stop":"Two couplings, one repeat and one finer coupled run; retain a failed tolerance.",
        "boundary":"Regional abstract oscillator states, not neuron voltages, EEG, patient anatomy, or a drug model."
    }
    out=new_run("brain_regions",protocol)
    c=connectivity.Connectivity.from_file()
    c.configure()
    c.weights=c.weights/max(float(c.weights.sum(axis=1).max()),1e-12)
    c.speed=np.array([3.])
    c.configure()
    count=c.number_of_regions
    initial=np.random.default_rng(42).uniform(-.5,.5,(2,count,1))
    np.savez_compressed(out/"connectome_and_initial.npz",weights=c.weights,tract_lengths_mm=c.tract_lengths,
                        centres=c.centres,region_labels=c.region_labels,initial_state=initial)
    model=models.Generic2dOscillator(a=np.array([2.]))
    model.configure()
    save_json(out/"oscillator_parameters.json",{key:getattr(model,key).tolist() for key in
                  ["tau","a","b","c","d","e","f","g","alpha","beta","gamma","I"]})
    def simulate(strength,dt):
        horizon=int(np.ceil(np.max(c.tract_lengths/3.)/dt))+2
        history=np.repeat(initial[np.newaxis,...],horizon,axis=0)
        sim=simulator.Simulator(model=models.Generic2dOscillator(a=np.array([2.])),
            connectivity=c,coupling=coupling.Linear(a=np.array([strength])),
            integrator=integrators.HeunDeterministic(dt=dt),
            monitors=(monitors.TemporalAverage(period=1.),),initial_conditions=history).configure()
        # TVB advances current_step by the supplied history length. Our history
        # is constant and represents times BEFORE the intervention, not elapsed
        # experimental time. Start at zero; the constant buffer needs no rotation.
        # This also starts each averaging window with a full set of new samples.
        sim.current_step=0
        ((t,data),)=sim.run(simulation_length=500.)
        return t,data[:,0,:,0]
    t,baseline=simulate(0,.1)
    tc,connected=simulate(.02,.1)
    tr,repeat=simulate(.02,.1)
    tf,finer=simulate(.02,.05)
    np.savez_compressed(out/"regional_traces.npz",time_ms=t,uncoupled=baseline,coupled=connected,
                        repeat=repeat,finer_time_ms=tf,finer=finer)
    csv_table(out/"coupled_regions.csv",["time_ms"]+c.region_labels.tolist(),np.column_stack((tc,connected)))
    use=t>=100
    # Align the returned monitor grids explicitly rather than assume timestamps.
    aligned=np.column_stack([np.interp(tc,tf,finer[:,i]) for i in range(count)])
    fine_error=float(np.sqrt(np.mean((connected[use]-aligned[use])**2)))
    repeat_error=float(np.max(np.abs(connected-repeat)))
    change=float(np.sqrt(np.mean((connected[use]-baseline[use])**2)))
    metrics={"regions":int(count),"coupling_trajectory_RMS_model_units":change,
             "repeat_max_abs_error":repeat_error,"finer_step_RMS_model_units":fine_error,
             "mean_spatial_SD_uncoupled":float(baseline[use].std(axis=1).mean()),
             "mean_spatial_SD_coupled":float(connected[use].std(axis=1).mean())}
    fig,axes=plt.subplots(2,2,figsize=(12,8),layout="constrained")
    im=axes[0,0].imshow(c.weights,aspect="auto",cmap="magma")
    axes[0,0].set(title="Structural weights (normalized)",xlabel="Source region index",ylabel="Target region index")
    fig.colorbar(im,ax=axes[0,0],label="Weight (relative)")
    im=axes[0,1].imshow(connected.T,aspect="auto",extent=[tc[0],tc[-1],count,0],cmap="coolwarm")
    axes[0,1].set(title="Coupled regional activity",xlabel="Time (ms)",ylabel="Region index")
    fig.colorbar(im,ax=axes[0,1],label="V (model units)")
    for index in range(3):
        axes[1,0].plot(t,baseline[:,index],"--",alpha=.6)
        axes[1,0].plot(tc,connected[:,index],label=str(c.region_labels[index]))
    axes[1,0].set(title="Three regions: solid coupled, dashed uncoupled",xlabel="Time (ms)",ylabel="V (model units)")
    axes[1,0].legend(fontsize=8)
    axes[1,1].plot(t,baseline.std(axis=1),label="uncoupled")
    axes[1,1].plot(tc,connected.std(axis=1),label="coupled")
    axes[1,1].axvline(100,color="grey",linestyle=":")
    axes[1,1].set(title="Regional differences, not a health score",xlabel="Time (ms)",ylabel="Across-region SD (model units)")
    axes[1,1].legend()
    fig.suptitle("76-region teaching simulation — no patient fit or EEG forward model")
    fig.savefig(out/"brain_regions.png",dpi=150)
    plt.close(fig)
    checks={"finite":bool(np.isfinite(connected).all() and np.isfinite(baseline).all() and np.isfinite(finer).all()),
            "time_origin_and_duration":bool(abs(t[0]-.5)<1e-9 and abs(t[-1]-499.5)<1e-9 and len(t)==500),
            "matching_time_grids":bool(np.array_equal(t,tc) and np.array_equal(tc,tr)),
            "deterministic_repeat":repeat_error<1e-12,"finer_step_tolerance":fine_error<.05}
    return finish(out,metrics,checks)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("lesson",choices=["channels","reactions","regions"])
    parser.add_argument("--prediction",default="",help="Your own prediction, saved before computation")
    args=parser.parse_args()
    USER_PREDICTION=args.prediction
    {"channels":hh_lesson,"reactions":reaction_lesson,"regions":region_lesson}[args.lesson]()
