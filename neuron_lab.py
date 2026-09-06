"""AI-assisted teaching experiment: firing threshold in a simple neuron model."""
from pathlib import Path
import json
import platform
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import brian2 as b

ROOT = Path(__file__).parent

def simulate(current_pa=250, dt_ms=0.1, duration_ms=1000):
    """Units: pA input, mV voltage, ms time. Fixed illustrative parameters."""
    b.start_scope()
    b.prefs.codegen.target = 'numpy'
    b.defaultclock.dt = dt_ms * b.ms
    cells = b.NeuronGroup(1,
        'dv/dt = (-(v - rest) + resistance * current) / tau : volt (unless refractory)',
        threshold='v >= threshold_v', reset='v = rest', refractory=2*b.ms,
        method='exact', namespace={'rest':-65*b.mV, 'threshold_v':-50*b.mV,
        'resistance':100*b.Mohm, 'current':current_pa*b.pA, 'tau':20*b.ms})
    cells.v = -65*b.mV
    voltage = b.StateMonitor(cells, 'v', record=True)
    spikes = b.SpikeMonitor(cells)
    b.run(duration_ms*b.ms)
    return (np.asarray(voltage.t/b.ms), np.asarray(voltage.v[0]/b.mV),
            np.asarray(spikes.t/b.ms))

def analytic_rate(current_pa):
    """Steady firing rate from exact threshold-crossing time + refractory period."""
    drive_mv = 0.1 * current_pa
    if drive_mv <= 15:
        return 0.0
    return 1000 / (2 + 20*np.log(drive_mv/(drive_mv-15)))

def run_experiment():
    out = ROOT/'results'
    out.mkdir(exist_ok=True)
    rows = []
    for dt in [0.1, 0.05]:
        for current in [0, 100, 140, 160, 200, 250, 300]:
            t,v,spikes = simulate(current,dt,2000)
            # First 500 ms excluded; report an explicit 1.5 second counting window.
            rate = float(np.sum(spikes >= 500)/1.5)
            rows.append(dict(current_pa=current,dt_ms=dt,rate_hz=rate,
                             analytic_hz=analytic_rate(current)))
    table = pd.DataFrame(rows)
    table.to_csv(out/'sweep.csv',index=False)
    t,v,spikes = simulate()
    pd.DataFrame({'time_ms':t,'voltage_mv':v}).to_csv(out/'voltage.csv',index=False)
    fig,axes = plt.subplots(1,2,figsize=(11,4),layout='constrained')
    axes[0].plot(t[t<200],v[t<200],color='#3b6e60')
    axes[0].axhline(-50,ls='--',color='gray',label='Threshold')
    axes[0].set(xlabel='Time (ms)',ylabel='Membrane voltage (mV)',title='250 pA input; spikes represented by resets')
    axes[0].legend()
    for dt,g in table.groupby('dt_ms'):
        axes[1].plot(g.current_pa,g.rate_hz,'o-',label=f'Simulation dt={dt} ms')
    g=table[table.dt_ms==0.05]
    axes[1].plot(g.current_pa,g.analytic_hz,'k--',label='Analytic steady rate')
    axes[1].set(xlabel='Input current (pA)',ylabel='Firing rate (Hz)',title='Input versus firing rate')
    axes[1].legend()
    fig.suptitle('Simulated leaky integrate-and-fire neuron; illustrative parameters')
    fig.savefig(out/'neuron.png',dpi=160)
    plt.close(fig)
    pivot=table.pivot(index='current_pa',columns='dt_ms',values='rate_hz')
    checks={'below_threshold_silent':bool((table[table.current_pa<150].rate_hz==0).all()),
            'max_dt_difference_hz':float(abs(pivot[0.1]-pivot[0.05]).max()),
            'max_analytic_difference_hz':float(abs(table.rate_hz-table.analytic_hz).max()),
            'python':platform.python_version(),'brian2':b.__version__,
            'data_origin':'simulation; no biological recordings'}
    (out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
    assert checks['below_threshold_silent']
    assert checks['max_dt_difference_hz'] <= 2
    assert checks['max_analytic_difference_hz'] <= 2
    print(table.to_string(index=False))
    print(json.dumps(checks,indent=2))
    return table

if __name__=='__main__':
    run_experiment()
