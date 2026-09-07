"""Local controls-first notebook interface. All scientific calculations stay in circuit_lab."""
from dataclasses import replace
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import json
import uuid

import ipywidgets as w
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from IPython.display import display, Markdown, clear_output

from circuit_lab import ROOT, Config, firing_trace, spectrum, load_run, run_comparison

LABELS = {"reference_control": "Reference / control", "reference_perturbed": "Reference / NMDA reduction",
          "variant_control": "Hypothesis / control", "variant_perturbed": "Hypothesis / NMDA reduction"}
COLORS = ["#3366aa", "#c06622", "#477660", "#975697"]


def figure_for(table, results, view="Population firing", cell="e"):
    names = list(LABELS)
    if view == "Matched differences":
        fig = make_subplots(rows=1, cols=2, subplot_titles=["Post-input firing change", "Pulse-minus-pre change"])
        for col, metric in enumerate([f"{cell}_post_hz", f"{cell}_pulse_minus_pre_hz"], 1):
            pivot = table.pivot(index="seed", columns="condition", values=metric)
            for j, group in enumerate(["reference", "variant"]):
                delta = pivot[f"{group}_perturbed"]-pivot[f"{group}_control"]
                fig.add_trace(go.Scatter(x=[group]*len(delta), y=delta, mode="markers",
                                        marker=dict(color=COLORS[j], size=7), showlegend=False,
                                        customdata=delta.index, hovertemplate="Seed %{customdata}: %{y:.3f} Hz<extra></extra>"), 1, col)
                fig.add_trace(go.Scatter(x=[group], y=[delta.mean()], mode="markers",
                                        marker=dict(symbol="diamond-open", size=13, color=COLORS[j]),
                                        error_y=dict(array=[delta.std(ddof=1) if len(delta)>1 else 0]),
                                        showlegend=False, hovertemplate="Mean %{y:.3f} Hz; bars = sample SD<extra></extra>"), 1, col)
            fig.add_hline(y=0, line_dash="dot", line_color="#777", row=1, col=col)
            fig.update_yaxes(title_text="Perturbed − control (Hz)", row=1, col=col)
        title = "Paired seeds • dots = runs; diamonds = mean<br>Bars = simulation SD, not patient uncertainty"
    else:
        fig = make_subplots(rows=2, cols=2, shared_xaxes="all", shared_yaxes="all",
                            subplot_titles=[LABELS[n] for n in names], vertical_spacing=.2)
        for j, name in enumerate(names):
            r = results[name]
            row, col = j//2+1, j%2+1
            if view == "Population firing":
                x, y = firing_trace(r, cell)
                fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=COLORS[j]), showlegend=False), row, col)
                x_label, y_label = "Time (ms)", "Rate per neuron (Hz)"
            elif view == "Spike raster":
                fig.add_trace(go.Scattergl(x=r[f"spike_t_{cell}"], y=r[f"spike_id_{cell}"], mode="markers",
                                          marker=dict(size=3, color=COLORS[j]), showlegend=False), row, col)
                x_label, y_label = "Time (ms)", "Neuron index"
            elif view == "Synaptic currents":
                for field, color in zip(["I_AMPA", "I_NMDA", "I_GABA", "I_external"], ["#3366aa", "#477660", "#c06622", "#975697"]):
                    fig.add_trace(go.Scatter(x=r["t_ms"], y=-r[f"{field}_{cell}"], name=field[2:],
                                            mode="lines", legendgroup=field, showlegend=(j==0),
                                            line=dict(color=color)), row, col)
                x_label, y_label = "Time (ms)", "Inward current, cell 0 (pA)"
            else:
                x, y = spectrum(r, cell)
                fig.add_trace(go.Scatter(x=x, y=y, mode="lines", line=dict(color=COLORS[j]), showlegend=False), row, col)
                fig.update_xaxes(range=[0, 120], row=row, col=col)
                x_label, y_label = "Frequency (Hz)", "Rate PSD (Hz²/Hz)"
            fig.update_xaxes(title_text=x_label, row=row, col=col)
            fig.update_yaxes(title_text=y_label, row=row, col=col)
            if view != "Power spectrum":
                fig.add_vrect(x0=r["config"]["stimulus_on_ms"], x1=r["config"]["stimulus_off_ms"],
                              opacity=.08, fillcolor="#777", line_width=0, row=row, col=col)
        title = f"{view} • {'excitatory' if cell=='e' else 'inhibitory'} cells • illustrative seed {results[names[0]]['config']['seed']}"
        if view == "Power spectrum":
            title += " • spike-count rate, NOT EEG"
    fig.update_layout(template="plotly_white", height=570, title=dict(text=title, font=dict(size=14)),
                      margin=dict(l=60, r=25, t=95, b=55), legend=dict(orientation="h", y=-.18),
                      hovermode="closest", font=dict(size=12))
    return fig


def evidence_records(query="", topic="All"):
    rows = json.loads((ROOT/"research"/"evidence.json").read_text(encoding="utf-8"))
    terms = query.lower().split()
    return [r for r in rows if (topic == "All" or r["topic"] == topic)
            and all(term in json.dumps(r).lower() for term in terms)]


def evidence_panel():
    search = w.Text(placeholder="Search BDNF, PTSD, mouse, null, acute…", description="Search", layout=w.Layout(width="95%"))
    topic = w.Dropdown(options=["All"]+sorted({r["topic"] for r in evidence_records()}), description="Topic")
    output = w.HTML()
    def refresh(_=None):
        rows = evidence_records(search.value, topic.value)
        parts = [f"<p>{len(rows)} evidence records. This is a scoped evidence map, not an exhaustive review.</p>"]
        for r in rows:
            parts.append(f'<details><summary><b>{escape(r["id"])}</b> · {escape(r["population"])} · {escape(r["finding"])}</summary>'
                         + "".join(f"<p><b>{escape(k.replace('_',' '))}:</b> {escape(str(v))}</p>" for k,v in r.items() if k not in ["id", "finding", "url"])
                         + f'<p><a href="{escape(r["url"], quote=True)}" target="_blank" rel="noopener">Read primary source</a></p></details><hr>')
        output.value = "".join(parts)
    search.observe(refresh, "value")
    topic.observe(refresh, "value")
    refresh()
    return w.VBox([search, topic, output])


def build_workbench():
    """Nothing runs automatically. Existing complete local runs are loaded if available."""
    learn = w.Output()
    with learn:
        display(Markdown((ROOT/"research"/"LEARN.md").read_text(encoding="utf-8")))
        display(Markdown("[Read the research path: small circuits, whole-brain models, and your next milestones](research/RESEARCH_PATH.md)"))
    fraction_e = w.FloatSlider(value=.1, min=0, max=1, step=.05, description="NMDA → E", readout_format=".2f", continuous_update=False)
    fraction_i = w.FloatSlider(value=.3, min=0, max=1, step=.05, description="NMDA → I", readout_format=".2f", continuous_update=False)
    variant = w.Dropdown(options=[("Inhibitory strength", "inhibition"), ("Recurrent excitation", "recurrent_excitation"), ("External input", "external_input")], description="Hypothesis")
    scale = w.FloatSlider(value=.85, min=.5, max=1.5, step=.05, description="Scale ×", continuous_update=False)
    seed_count = w.Dropdown(options=[("Preview: 1 seed", 1), ("Compare: 3 seeds", 3), ("Check: 5 seeds", 5)], value=3, description="Repeats")
    dt = w.Dropdown(options=[.1, .05, .025], value=.1, description="Step (ms)")
    stimulus = w.FloatSlider(value=150, min=0, max=500, step=25, description="Pulse (pA)", continuous_update=False)
    size = w.Dropdown(options=[("100 cells: 80 E + 20 I", 100), ("250 cells: 200 E + 50 I", 250),
                               ("500 cells: 400 E + 100 I", 500)], value=100, description="Size")
    advanced = w.Accordion(children=[w.VBox([seed_count, dt, stimulus, size,
        w.HTML("<p>Size tests finite-population effects, not brain completeness. Larger runs are slower; weights scale inversely with population size.</p>")])],
        titles=("Advanced: numerical step, repeats, test input, size",))
    advanced.selected_index = None
    prediction = w.Textarea(placeholder="Before running: what changes do you predict, and what would contradict your idea?", layout=w.Layout(width="98%", height="70px"))
    run = w.Button(description="Run comparison", button_style="primary", icon="play")
    status = w.HTML("<p>Ready. Controls are assumptions, not clinical doses. A run may take a few minutes.</p>")
    view = w.Dropdown(options=["Population firing", "Spike raster", "Synaptic currents", "Power spectrum", "Matched differences"], description="View")
    cell = w.Dropdown(options=[("Excitatory", "e"), ("Inhibitory", "i")], description="Cells")
    plot = w.Output()
    caption = w.HTML()
    notes = w.Textarea(placeholder="After running: explain the result, a limitation, and your next test.", layout=w.Layout(width="98%", height="70px"))
    save = w.Button(description="Save interpretation", icon="save")
    state = {"bundle": None}
    def redraw(_=None):
        with plot:
            clear_output(wait=True)
            if state["bundle"]:
                table, results, folder = state["bundle"]
                display(figure_for(table, results, view.value, cell.value))
                manifest = json.loads((folder/"manifest.json").read_text(encoding="utf-8"))
                c = manifest["configurations"]["reference_perturbed"]
                caption.value = (f'<p><b>Displayed saved run:</b> {escape(folder.name)} · bE={c["block_e"]}, bI={c["block_i"]} · '
                                 f'{escape(manifest["variant"])} × {manifest["variant_scale"]} · {c["n_e"] + c["n_i"]} cells · {len(manifest["seeds"])} seed(s) · dt={c["dt_ms"]} ms · pulse={c["stimulus_pa"]} pA.</p>'
                                 '<p>Other views show the first seed; Matched differences shows all seeds. No confidence interval for real people is implied.</p>')
    def changed(_):
        status.value = "<p>Controls changed. Plots still show the saved run identified below; click Run comparison to calculate new results.</p>"
    def execute(_):
        if not prediction.value.strip():
            status.value = "<p>Please record a prediction first—even ‘I do not know yet’ is useful.</p>"
            return
        run.disabled = True
        try:
            base = Config(n_e=size.value*4//5, n_i=size.value//5, block_e=fraction_e.value,
                          block_i=fraction_i.value, dt_ms=dt.value, stimulus_pa=stimulus.value)
            state["bundle"] = run_comparison(base, seeds=(11,22,33,44,55)[:seed_count.value],
                                               variant=variant.value, variant_scale=scale.value, prediction=prediction.value,
                                               progress=lambda msg: setattr(status, "value", f"<p>Running {escape(msg)}…</p>"))
            redraw()
            status.value = "<p>Complete and saved locally. Inspect Matched differences, then write your interpretation.</p>"
        except Exception as error:
            status.value = f"<p>Run failed: {escape(str(error))}. Previous displayed results are unchanged; check the run manifest.</p>"
        finally:
            run.disabled = False
    def save_notes(_):
        if not state["bundle"] or not notes.value.strip():
            status.value = "<p>Load/run an experiment and write an interpretation first.</p>"
            return
        folder = state["bundle"][2]
        path = folder/f"learner-note-{uuid.uuid4().hex[:8]}.json"
        path.write_text(json.dumps({"recorded_utc": datetime.now(timezone.utc).isoformat(), "text": notes.value}, indent=2), encoding="utf-8")
        status.value = f"<p>Saved a new note to {escape(path.name)}. Earlier notes were preserved.</p>"
    for control in [fraction_e, fraction_i, variant, scale, seed_count, dt, stimulus, size]:
        control.observe(changed, "value")
    run.on_click(execute)
    save.on_click(save_notes)
    view.observe(redraw, "value")
    cell.observe(redraw, "value")
    candidates = sorted((ROOT/"results"/"circuit").glob("*/manifest.json"), reverse=True)
    # Prefer the standard example over a later numerical/no-input verification run.
    def preferred(path):
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
            return manifest["configurations"]["reference_perturbed"] == Config(block_e=.1, block_i=.3).__dict__
        except (OSError, ValueError, KeyError):
            return False
    candidates.sort(key=preferred, reverse=True)
    for path in candidates:
        try:
            state["bundle"] = load_run(path.parent)
            break
        except (ValueError, OSError, KeyError):
            continue
    redraw()
    experiment = w.VBox([w.HTML("<h3>One circuit question at a time</h3><p>Fractional NMDA conductance reduction; no dose mapping. Hypothesis variants are not validated PTSD brains.</p>"),
                         w.HBox([fraction_e, fraction_i], layout=w.Layout(flex_flow="row wrap")),
                         w.HBox([variant, scale], layout=w.Layout(flex_flow="row wrap")), advanced,
                         prediction, run, status, w.HBox([view, cell], layout=w.Layout(flex_flow="row wrap")),
                         caption, plot, notes, save])
    tabs = w.Tab(children=[learn, experiment, evidence_panel()], titles=("Learn", "Experiment", "Evidence"))
    tabs.selected_index = 1
    return tabs


def save_static_summary(table, results, folder):
    """Portable figure generated from exactly the same saved results as the notebook."""
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    for j, (name, r) in enumerate(results.items()):
        t, rate = firing_trace(r)
        axes[0,0].plot(t, rate, lw=.8, alpha=.85, color=COLORS[j], label=LABELS[name])
        f, p = spectrum(r)
        axes[0,1].plot(f, p, lw=1, color=COLORS[j])
    example = results["reference_perturbed"]
    for field, color in zip(["I_AMPA", "I_NMDA", "I_GABA"], COLORS):
        axes[1,0].plot(example["t_ms"], -example[field+"_e"], lw=.8, color=color, label=field[2:])
    pivot = table.pivot(index="seed", columns="condition", values="e_post_hz")
    for j, group in enumerate(["reference", "variant"]):
        delta = pivot[group+"_perturbed"]-pivot[group+"_control"]
        axes[1,1].scatter([j]*len(delta), delta, color=COLORS[j])
        axes[1,1].errorbar(j, delta.mean(), yerr=delta.std(ddof=1) if len(delta)>1 else 0, fmt="D", color="black", capsize=4)
    axes[1,1].axhline(0, color="gray", ls="--", lw=.8)
    axes[1,1].set(xticks=[0,1], xticklabels=["Reference", "Hypothesis"], ylabel="Paired post-input change (Hz)")
    axes[0,0].set(title="Excitatory firing • illustrative first seed", ylabel="Rate per neuron (Hz)")
    axes[0,0].legend(fontsize=8, loc="upper right")
    axes[0,1].set(title="Population rate spectrum • NOT EEG", xlim=(0,120), xlabel="Frequency (Hz)", ylabel="PSD (Hz²/Hz)")
    axes[1,0].set(title="Example excitatory cell • reference + reduction", xlabel="Time (ms)", ylabel="Inward synaptic current (pA)")
    axes[1,0].legend(fontsize=8)
    axes[1,1].set_title("All seeds • mean and sample SD")
    fig.suptitle("Teaching NMDA circuit • simulated data, not a human or PTSD prediction", fontsize=13)
    fig.savefig(Path(folder)/"overview.png", dpi=140)
    plt.close(fig)
