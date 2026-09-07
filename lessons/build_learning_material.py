"""Generate study notebooks and installed-environment receipts; no simulations."""
from pathlib import Path
import json
import subprocess
import nbformat as nb

ROOT=Path(__file__).resolve().parents[1]

LESSONS=[
    ("03_ion_channels.ipynb","Ion channels: what creates a spike?","science-workbench","Science Workbench",
     "ion_channels","ion_channels.png","hh_lesson","hh_trace",
     "The top plot is membrane voltage. The middle plot separates sodium, potassium and leak currents. "
     "The bottom plot shows the m, h and n gate variables. Grey shading marks the input pulse. "
     "Negative sodium current means inward positive charge under this sign convention; it is not a negative emotion.",
     "Before changing anything, explain why m rising and h falling have different effects. "
     "Then predict whether half of the sodium conductance means half the number of spikes. "
     "Read hh_rates and hh_trace, and reproduce the m-infinity calculation at -65 mV yourself."),
    ("04_reaction_networks.ipynb","Reaction networks: when a shortcut stops matching","science-biochem","Science - Tellurium",
     "reaction_network","reaction_network.png","reaction_lesson","reaction_lesson",
     "Each row uses a different total enzyme concentration. On the left, substrate becomes product through "
     "a temporarily bound complex. On the right, solid lines are the full reaction model and dashed lines "
     "are the reduced equation. A larger gap means the approximation differs more; it does not mean the solver broke.",
     "Write the four derivatives from the three reactions. Show that d(E+ES)/dt=0 and "
     "d(S+ES+P)/dt=0. Explain why binding temporarily hides substrate from the free-substrate pool. "
     "Predict the effect of setting kcat=0 before making a separate copy of the experiment."),
    ("05_brain_regions.ipynb","Brain regions: connected populations, not individual cells","science-tvb","Science - TVB",
     "brain_regions","brain_regions.png","region_lesson","region_lesson",
     "The weight matrix describes regional connections. The heatmap shows one abstract state per region "
     "over time. The lower plots compare coupled and uncoupled systems. Similar lines are a result, not a "
     "broken display. These are not EEG measurements, emotional states, or a map of a particular person's brain.",
     "Identify the shape of the saved weights, initial state and trace arrays. Calculate one incoming "
     "weighted sum by hand. Explain why 76 regional oscillators are not 76 neurons. "
     "Write a prediction about changing a connection before editing one in a separate experiment.")
]

for filename,title,kernel,display,kind,figure,function,source,reading,exercise in LESSONS:
    cells=[nb.v4.new_markdown_cell(f"# {title}\n\nLocal teaching experiment, not validated clinical research. "
        f"Use the **{display}** kernel. Run → Run All Cells initially shows saved results without launching a new simulation. "
        "Read [the tool guide](research/TOOLS_AND_LESSONS.md) alongside this notebook."),
        nb.v4.new_code_cell("from pathlib import Path\nimport sys, json, inspect\nfrom IPython.display import display, Image, Markdown\n"
            "root = Path.cwd()\nassert (root / 'lessons' / 'run.py').exists(), 'Open this notebook from the science-workbench folder.'\n"
            "sys.path.insert(0, str(root / 'lessons'))\nimport run as lab\nprint('Python:', sys.executable)\n"),
        nb.v4.new_markdown_cell("## Read the saved experiment\n\n"+reading),
        nb.v4.new_code_cell(f"runs = []\nfor manifest in (root / 'results' / 'multiscale').glob('*/manifest.json'):\n"
            "    item = json.loads(manifest.read_text(encoding='utf-8'))\n"
            f"    if item['lesson'] == '{kind}' and item['status'] == 'passed':\n"
            "        runs.append(manifest.parent)\n"
            "assert runs, 'No completed example found; follow the reproduction command in the guide.'\n"
            "saved = sorted(runs)[-1]\nprint(saved)\n"
            f"display(Image(filename=str(saved / '{figure}')))\n"
            "display(json.loads((saved / 'metrics.json').read_text(encoding='utf-8')))\n"
            "display(json.loads((saved / 'checks.json').read_text(encoding='utf-8')))"),
        nb.v4.new_markdown_cell("## Own the calculation\n\n"+exercise+"\n\n"
            "Keep your own prediction, edits and interpretation. The initial code and runs were AI-assisted; "
            "being able to reproduce and explain them is the learning goal."),
        nb.v4.new_code_cell(f"print(inspect.getsource(lab.{source}))"),
        nb.v4.new_markdown_cell("## Run a fresh copy when ready\n\nFirst write your prediction. "
            "Change RUN_NEW to True only when you want a new fixed-protocol run. It creates a new folder and never replaces the example."),
        nb.v4.new_code_cell("RUN_NEW = False\nmy_prediction = ''\n"
            "if RUN_NEW:\n    assert my_prediction.strip(), 'Write your own prediction first.'\n"
            "    lab.USER_PREDICTION = my_prediction\n"
            f"    new_result = lab.{function}()\n"
            f"    display(Image(filename=str(new_result / '{figure}')))\n"
            "else:\n    print('Saved example only. No new simulation requested.')"),
        nb.v4.new_markdown_cell("## My notes\n\nPrediction:\n\nWhat I changed:\n\n"
            "What the result shows:\n\nWhat it cannot tell me:\n\nOne thing I can now explain without help:\n")]
    notebook=nb.v4.new_notebook(cells=cells,metadata={"kernelspec":{"name":kernel,"display_name":display,"language":"python"}})
    nb.validate(notebook)
    path=ROOT/filename
    if path.exists():
        raise FileExistsError(f"Not overwriting a study notebook that might contain notes: {path}")
    nb.write(notebook,path)
    print(path)

# These generated receipts pin installed versions, not upstream wheel hashes.
for folder,name in [(".venv-biochem","requirements-biochem-lock.txt"),(".venv-tvb","requirements-tvb-lock.txt")]:
    command=["uv","pip","freeze","--python",str(ROOT/folder/"Scripts"/"python.exe")]
    result=subprocess.run(command,check=True,capture_output=True,text=True)
    (ROOT/name).write_text("# Python 3.12.13, Windows x86-64; generated environment receipt\n"+result.stdout,encoding="utf-8")
    print(ROOT/name)
