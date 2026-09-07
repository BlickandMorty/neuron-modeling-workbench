"""Verify the installed NEURON runtime with a small compartmental simulation."""

import json
from pathlib import Path

from neuron import h


def run_verification() -> dict[str, float | int | str]:
    h.load_file("stdrun.hoc")

    mechanism_dll = Path(__file__).parent / "mechanisms" / "nrnmech.dll"
    custom_mechanism = "not built"
    if mechanism_dll.exists():
        h.nrn_load_dll(str(mechanism_dll.resolve()))
        mechanism_test = h.Section(name="mechanism_test")
        mechanism_test.insert("linearleak")
        custom_mechanism = "linearleak loaded"

    soma = h.Section(name="soma")
    dendrite = h.Section(name="dendrite")
    dendrite.connect(soma(1))

    soma.L = soma.diam = 20
    soma.nseg = 1
    soma.insert("hh")

    dendrite.L = 200
    dendrite.diam = 2
    dendrite.nseg = 21
    dendrite.insert("pas")

    stimulus = h.IClamp(soma(0.5))
    stimulus.delay = 5
    stimulus.dur = 1
    stimulus.amp = 0.5

    time = h.Vector().record(h._ref_t)
    soma_voltage = h.Vector().record(soma(0.5)._ref_v)
    dendrite_voltage = h.Vector().record(dendrite(1)._ref_v)

    h.finitialize(-65)
    h.continuerun(20)

    result = {
        "neuron_version": h.nrnversion(),
        "samples": len(time),
        "soma_peak_mv": float(max(soma_voltage)),
        "dendrite_peak_mv": float(max(dendrite_voltage)),
        "end_time_ms": float(h.t),
        "custom_mechanism": custom_mechanism,
    }
    assert result["samples"] == 801
    assert result["soma_peak_mv"] > 0
    assert result["dendrite_peak_mv"] > -40
    assert abs(result["end_time_ms"] - 20) < 1e-9
    if mechanism_dll.exists():
        assert result["custom_mechanism"] == "linearleak loaded"
    return result


if __name__ == "__main__":
    output = run_verification()
    destination = Path("results") / "neuron_install_verification.json"
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(output, indent=2) + "\n", encoding="ascii")
    print(json.dumps(output, indent=2))
    print(f"Saved {destination}")
