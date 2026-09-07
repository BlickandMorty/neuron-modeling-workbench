"""Build checked, anatomy-aware views from the saved regional teaching run."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import nbformat as nb
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "multiscale"
OUTPUT = ROOT / "results" / "visual_bridge"
NOTEBOOK = ROOT / "07_numbers_to_brain_maps.ipynb"


def latest_region_run() -> Path:
    candidates = []
    for manifest_path in RESULTS.glob("*/manifest.json"):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("lesson") == "brain_regions" and manifest.get("status") == "passed":
            candidates.append(manifest_path.parent)
    if not candidates:
        raise FileNotFoundError("No passed brain-regions teaching run was found.")
    return sorted(candidates)[-1]


def strongest_edges(weights: np.ndarray, limit: int = 120) -> list[tuple[int, int]]:
    pairs = np.argwhere(weights > 0)
    ranked = sorted(pairs, key=lambda pair: weights[tuple(pair)], reverse=True)
    return [(int(source), int(target)) for target, source in ranked[:limit]]


def draw_projection(
    ax: plt.Axes,
    centres: np.ndarray,
    weights: np.ndarray,
    values: np.ndarray,
    axes: tuple[int, int],
    title: str,
    value_limit: float,
):
    for source, target in strongest_edges(weights):
        ax.plot(
            centres[[source, target], axes[0]],
            centres[[source, target], axes[1]],
            color="#a7a7a7",
            alpha=0.12,
            linewidth=0.6,
            zorder=1,
        )
    points = ax.scatter(
        centres[:, axes[0]],
        centres[:, axes[1]],
        c=values,
        cmap="coolwarm",
        vmin=-value_limit,
        vmax=value_limit,
        s=54,
        edgecolor="#202020",
        linewidth=0.35,
        zorder=2,
    )
    ax.set_title(title)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_axis_off()
    return points


def build_outputs() -> tuple[Path, Path, Path]:
    source = latest_region_run()
    connectome = np.load(source / "connectome_and_initial.npz", allow_pickle=False)
    traces = np.load(source / "regional_traces.npz", allow_pickle=False)
    centres = connectome["centres"]
    labels = connectome["region_labels"]
    weights = connectome["weights"]
    time_ms = traces["time_ms"]
    coupled = traces["coupled"]

    if centres.shape != (76, 3) or coupled.shape != (500, 76):
        raise ValueError(f"Unexpected saved shapes: centres={centres.shape}, activity={coupled.shape}")
    if not np.isfinite(centres).all() or not np.isfinite(coupled).all():
        raise ValueError("The saved visualization inputs contain non-finite values.")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    value_limit = float(np.max(np.abs(coupled)))
    frame_indices = np.linspace(0, len(time_ms) - 1, 4, dtype=int)

    fig = plt.figure(figsize=(11, 8))
    grid = fig.add_gridspec(2, 3, width_ratios=(1, 1, 0.045), wspace=0.08, hspace=0.18)
    axes = np.asarray(
        [
            [fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1])],
            [fig.add_subplot(grid[1, 0]), fig.add_subplot(grid[1, 1])],
        ]
    )
    colorbar_ax = fig.add_subplot(grid[:, 2])
    for ax, index in zip(axes.flat, frame_indices):
        points = draw_projection(
            ax,
            centres,
            weights,
            coupled[index],
            (0, 2),
            f"Regional state at {time_ms[index]:.1f} ms",
            value_limit,
        )
    fig.suptitle(
        "Saved 76-region model in anatomical coordinate space\n"
        "Color = abstract regional state (model units), not voltage, current, EEG, or measured brain activity",
        fontsize=13,
    )
    colorbar = fig.colorbar(points, cax=colorbar_ax)
    colorbar.ax.set_title("State\n(model units)", fontsize=9, pad=8)
    fig.subplots_adjust(left=0.03, right=0.94, bottom=0.03, top=0.88)
    static_path = OUTPUT / "regional_activity_snapshots.png"
    fig.savefig(static_path, dpi=180)
    plt.close(fig)

    fig = plt.figure(figsize=(11, 4.8))
    animation_grid = fig.add_gridspec(1, 3, width_ratios=(1, 1, 0.045), wspace=0.08)
    front_ax = fig.add_subplot(animation_grid[0, 0])
    side_ax = fig.add_subplot(animation_grid[0, 1])
    animation_colorbar_ax = fig.add_subplot(animation_grid[0, 2])
    front_points = draw_projection(
        front_ax, centres, weights, coupled[0], (0, 2), "Front projection", value_limit
    )
    side_points = draw_projection(
        side_ax, centres, weights, coupled[0], (1, 2), "Side projection", value_limit
    )
    title = fig.suptitle("")
    colorbar = fig.colorbar(side_points, cax=animation_colorbar_ax)
    colorbar.ax.set_title("State\n(model units)", fontsize=9, pad=8)
    fig.text(
        0.5,
        0.015,
        "Teaching model: colors are simulated regional population states, not electrical current or a recording.",
        ha="center",
        fontsize=9,
    )
    fig.subplots_adjust(left=0.02, right=0.94, bottom=0.10, top=0.86)

    animation_indices = np.arange(0, len(time_ms), 10)

    def update(frame_index: int):
        data_index = int(animation_indices[frame_index])
        values = coupled[data_index]
        front_points.set_array(values)
        side_points.set_array(values)
        title.set_text(f"Regional-state evolution at {time_ms[data_index]:.1f} ms")
        return front_points, side_points, title

    movie = animation.FuncAnimation(
        fig,
        update,
        frames=len(animation_indices),
        interval=90,
        blit=False,
    )
    gif_path = OUTPUT / "regional_activity.gif"
    movie.save(gif_path, writer=animation.PillowWriter(fps=11))
    plt.close(fig)

    receipt = {
        "source_run": str(source.relative_to(ROOT)),
        "centres_shape": list(centres.shape),
        "activity_shape": list(coupled.shape),
        "time_range_ms": [float(time_ms[0]), float(time_ms[-1])],
        "region_count": int(len(labels)),
        "animation_frames": int(len(animation_indices)),
        "value_limit_model_units": value_limit,
        "interpretation_boundary": (
            "An anatomy-aware display of a saved abstract regional oscillator model; "
            "not membrane voltage, electric current, EEG, fMRI, or patient data."
        ),
    }
    receipt_path = OUTPUT / "visualization_receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="ascii")
    return static_path, gif_path, receipt_path


def build_notebook():
    if NOTEBOOK.exists():
        print(f"Preserved existing study notebook: {NOTEBOOK}")
        return
    cells = [
        nb.v4.new_markdown_cell(
            "# From numbers to brain maps\n\n"
            "Use the **Science - TVB** kernel. This lesson reads a saved, checked run; "
            "it does not launch a new simulation. Its purpose is to connect array shapes, "
            "units, anatomical coordinates, plots, and defensible interpretation."
        ),
        nb.v4.new_code_cell(
            "from pathlib import Path\n"
            "import json\n"
            "import numpy as np\n"
            "from IPython.display import Image, display\n\n"
            "root = Path.cwd()\n"
            "receipt = json.loads((root / 'results' / 'visual_bridge' / 'visualization_receipt.json').read_text())\n"
            "receipt"
        ),
        nb.v4.new_markdown_cell(
            "## Read the visual grammar\n\n"
            "- A **row** in the activity array is one time point.\n"
            "- A **column** is one modeled region.\n"
            "- A region's three coordinates choose where its dot appears.\n"
            "- The structural matrix chooses which dots receive faint connecting lines.\n"
            "- Color encodes the model variable at that time. It does not turn that variable into voltage.\n"
            "- Apparent motion means the regional states changed over time; it is not a movie of charge physically traveling."
        ),
        nb.v4.new_code_cell(
            "display(Image(filename=str(root / 'results' / 'visual_bridge' / 'regional_activity_snapshots.png')))"
        ),
        nb.v4.new_code_cell(
            "display(Image(filename=str(root / 'results' / 'visual_bridge' / 'regional_activity.gif')))"
        ),
        nb.v4.new_markdown_cell(
            "## Reconstruct the mapping yourself\n\n"
            "Load `connectome_and_initial.npz` and `regional_traces.npz` from the source run "
            "listed in the receipt. Print every array shape. Pick one time index and one region. "
            "Confirm that the dot's color comes from `coupled[time_index, region_index]` and its "
            "position comes from `centres[region_index]`. Then draw only ten regions without "
            "copying the builder. That is the shortest path from seeing a picture to understanding it."
        ),
        nb.v4.new_markdown_cell(
            "## Design your own experiment\n\n"
            "Write a question and prediction first. Change exactly one factor, such as one edge weight, "
            "global coupling, conduction speed, initial state, or the regional equations. Keep the baseline. "
            "Choose a numerical measure before viewing the result. A useful first measure is the time of the "
            "largest response per region relative to the stimulated region. Call it latency only if the model "
            "contains a defined perturbation and propagation mechanism. Compare coupled, uncoupled, and finer-step controls."
        ),
        nb.v4.new_markdown_cell(
            "## My explanation\n\n"
            "What each axis means:\n\nWhat the color means:\n\n"
            "What changed over time:\n\nWhat the model can support:\n\n"
            "What the picture cannot support:\n\nOne numerical check I performed myself:"
        ),
    ]
    notebook = nb.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {
                "display_name": "Science - TVB",
                "language": "python",
                "name": "science-tvb",
            },
            "language_info": {"name": "python", "version": "3.12"},
        },
    )
    nb.validate(notebook)
    nb.write(notebook, NOTEBOOK)


if __name__ == "__main__":
    static, gif, receipt = build_outputs()
    build_notebook()
    print(static)
    print(gif)
    print(receipt)
    print(NOTEBOOK)
