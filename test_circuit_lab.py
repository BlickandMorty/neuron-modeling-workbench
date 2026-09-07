"""Run with python -m unittest -v test_circuit_lab. No patient data or network access."""
from dataclasses import replace
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

import brian2 as b
import numpy as np
import nbformat
from circuit_lab import Config, conditions, simulate, metrics, firing_trace, spectrum, nmda_voltage_factor, run_comparison, load_run


SMALL = Config(n_e=8, n_i=2, duration_ms=200, stimulus_on_ms=80, stimulus_off_ms=100)


class ConfigurationTests(unittest.TestCase):
    def test_fixed_size_protocol(self):
        from size_sensitivity import size_config
        for total in (100, 250, 500):
            config = size_config(total)
            config.validate()
            self.assertEqual(config.n_e + config.n_i, total)
            self.assertEqual(config.n_e, 4*config.n_i)
        with self.assertRaises(ValueError):
            size_config(1000)

    def test_size_summary_uses_each_seed(self):
        import pandas as pd
        from size_sensitivity import summarize
        table = pd.DataFrame([dict(cells=100, condition="test", seed=s, e_post_hz=r, i_post_hz=2*r)
                              for s, r in zip((11,22,33), (1.,2.,3.))])
        summary = summarize(table).set_index("cell")
        self.assertEqual(summary.loc["e", "mean_hz"], 2)
        self.assertEqual(summary.loc["e", "sd_hz"], 1)
        self.assertEqual(summary.loc["i", "mean_hz"], 4)
        self.assertEqual(summary.loc["i", "seeds"], 3)

    def test_invalid_values(self):
        for change in [{"block_e": -1}, {"block_i": 1.1}, {"dt_ms": 0}, {"seed": 1.5},
                       {"n_e": 0}, {"external_scale": float("nan")}, {"stimulus_off_ms": 300},
                       {"record_ms": .55}, {"seed": True}, {"inhibition_scale": 3}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                replace(SMALL, **change).validate()

    def test_one_factor_changes(self):
        for name, field in [("inhibition", "inhibition_scale"), ("recurrent_excitation", "excitation_scale"), ("external_input", "external_scale")]:
            cases = conditions(Config(block_e=.1, block_i=.3), name, .85)
            self.assertEqual(getattr(cases["variant_control"], field), .85)
            self.assertEqual(cases["reference_control"].block_e, 0)
            self.assertEqual(cases["variant_perturbed"].block_i, .3)
            for other in {"excitation_scale", "inhibition_scale", "external_scale"}-{field}:
                self.assertEqual(getattr(cases["variant_control"], other), 1)

    def test_zero_and_identity_configs(self):
        cases = conditions(Config(), variant_scale=1)
        self.assertEqual(len(set(cases.values())), 1)

    def test_voltage_block_and_units(self):
        self.assertLess(nmda_voltage_factor(-70), nmda_voltage_factor(-20))
        self.assertAlmostEqual(float((500*b.pF/(25*b.nS))/b.ms), 20)
        self.assertAlmostEqual(float((150*b.pA/(500*b.pF))/(b.mV/b.ms)), .3)


class SimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.first = simulate(SMALL)
        cls.second = simulate(SMALL)

    def test_fixed_seed_exact_repeat(self):
        for key in self.first:
            if isinstance(self.first[key], np.ndarray):
                np.testing.assert_array_equal(self.first[key], self.second[key])

    def test_physical_bounds(self):
        for label in ["e", "i"]:
            self.assertTrue(np.isfinite(self.first[f"v_{label}"]).all())
            self.assertTrue((self.first[f"gate_{label}"] >= 0).all())
            self.assertTrue((self.first[f"gate_{label}"] <= 1).all())

    def test_no_drive_no_spikes(self):
        quiet = simulate(replace(SMALL, external_scale=0, stimulus_pa=0))
        self.assertEqual(len(quiet["spike_t_e"])+len(quiet["spike_t_i"]), 0)
        for label in ["e", "i"]:
            np.testing.assert_array_equal(quiet[f"I_NMDA_{label}"], 0)

    def test_full_block_removes_nmda_current(self):
        blocked = simulate(replace(SMALL, block_e=1, block_i=1))
        for label in ["e", "i"]:
            np.testing.assert_array_equal(blocked[f"I_NMDA_{label}"], 0)

    def test_only_targeted_current_is_removed(self):
        blocked = simulate(replace(SMALL, block_e=1, block_i=0, stimulus_pa=500))
        np.testing.assert_array_equal(blocked["I_NMDA_e"], 0)
        self.assertGreater(float(np.max(np.abs(blocked["I_NMDA_i"]))), 0)

    def test_spike_count_rate_integral(self):
        t, rate = firing_trace(self.first)
        self.assertAlmostEqual(float(np.sum(rate)*.005*SMALL.n_e), len(self.first["spike_t_e"]))

    def test_short_psd_unavailable_not_zero(self):
        self.assertEqual(len(spectrum(self.first)[0]), 0)
        self.assertIsNone(metrics(self.first)["e_30_90_power_hz2"])

    def test_actual_synaptic_decay_between_events(self):
        # Infer conductance from the actual simulator's I=g(V-E) traces.
        # Exclude intervals containing arrivals, including the 0.5-ms synaptic delay.
        t = self.first["t_ms"]
        for field, source, tau, reversal in [("I_AMPA", "e", 2., 0.), ("I_GABA", "i", 5., -70.)]:
            voltage = self.first["v_e"] - reversal
            conductance = np.divide(self.first[field+"_e"], voltage,
                                    out=np.zeros_like(voltage), where=np.abs(voltage)>1e-9)
            arrivals = self.first[f"spike_t_{source}"] + .5
            selected = [j for j in range(len(t)-1) if conductance[j]>1e-8
                        and abs(voltage[j+1])>1e-9
                        and not np.any((arrivals >= t[j]-.001) & (arrivals <= t[j+1]+.001))]
            self.assertGreater(len(selected), 0)
            factor = (1-SMALL.dt_ms/tau)**round(SMALL.record_ms/SMALL.dt_ms)
            np.testing.assert_allclose(conductance[np.array(selected)+1], conductance[selected]*factor, rtol=1e-9, atol=1e-9)

    def test_psd_identifies_known_signal(self):
        # Deterministic spike-count modulation provides a frequency-axis sanity check.
        t = np.arange(2000)
        counts = np.rint(20+10*np.sin(2*np.pi*50*t/1000)).astype(int)
        synthetic = {"config": Config().__dict__, "spike_t_e": np.repeat(t+.5, counts)}
        f, p = spectrum(synthetic)
        self.assertLess(abs(float(f[np.argmax(p)])-50), 4.)


class ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = simulate(SMALL)

    def test_save_load_and_tamper_detection(self):
        with tempfile.TemporaryDirectory(prefix="circuit-tests-") as folder:
            with patch("circuit_lab.simulate", return_value=self.sample):
                table, traces, path = run_comparison(SMALL, seeds=[11], output_root=folder)
            table2, traces2, _ = load_run(path)
            self.assertEqual(len(table2), 4)
            np.testing.assert_array_equal(traces2["reference_control"]["v_e"], self.sample["v_e"])
            (path/"metrics.csv").write_text("tampered test fixture", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_run(path)

    def test_failed_run_preserved(self):
        with tempfile.TemporaryDirectory(prefix="circuit-tests-") as folder:
            with patch("circuit_lab.simulate", side_effect=RuntimeError("test failure")):
                with self.assertRaises(RuntimeError):
                    run_comparison(SMALL, seeds=[11], output_root=folder)
            manifest = json.loads(next(Path(folder).glob("*/manifest.json")).read_text())
            self.assertEqual(manifest["status"], "failed")

    def test_evidence_schema_and_cohort_deduplication(self):
        from notebook_ui import evidence_records
        rows = evidence_records()
        self.assertEqual(len(rows), len({r["id"] for r in rows}))
        required = {"id", "topic", "title", "authors", "date", "population", "formulation_route", "exposure_context", "measurement_time", "finding", "uncertainty", "model_parameter", "cohort_id", "source_access", "url"}
        self.assertTrue(all(required <= set(r) for r in rows))
        shared = [r for r in rows if r["cohort_id"] == "yale-retrieval-exposure-pilot"]
        self.assertEqual(len(shared), 2)
        self.assertTrue(evidence_records("BDNF"))
        self.assertFalse(evidence_records("nonexistent-random-string"))

    def test_notebook_valid(self):
        notebook = nbformat.read(Path(__file__).parent/"02_ketamine_circuit.ipynb", as_version=4)
        nbformat.validate(notebook)

    def test_figures_match_saved_arrays_and_all_conditions(self):
        from notebook_ui import figure_for
        import pandas as pd
        results = {name: self.sample for name in conditions(SMALL)}
        table = pd.DataFrame([{"condition": name, "seed": 11, **metrics(self.sample)} for name in results])
        for view in ["Population firing", "Spike raster", "Synaptic currents", "Power spectrum", "Matched differences"]:
            figure = figure_for(table, results, view)
            self.assertGreater(len(figure.data), 0)
        figure = figure_for(table, results, "Population firing")
        self.assertEqual(len(figure.data), 4)
        np.testing.assert_array_equal(figure.data[0].y, firing_trace(self.sample)[1])

    def test_widget_controls_reach_calculation_and_stale_warning(self):
        from notebook_ui import build_workbench
        import ipywidgets as widgets
        with patch("notebook_ui.display"), patch("notebook_ui.clear_output"):
            tabs = build_workbench()
            def flatten(widget):
                yield widget
                for child in getattr(widget, "children", []):
                    yield from flatten(child)
            all_controls = list(flatten(tabs.children[1]))
            lookup = {getattr(x, "description", ""): x for x in all_controls if getattr(x, "description", "")}
            lookup["NMDA → E"].value = .2
            lookup["NMDA → I"].value = .4
            lookup["Hypothesis"].value = "external_input"
            lookup["Scale ×"].value = 1.2
            lookup["Step (ms)"].value = .05
            lookup["Pulse (pA)"].value = 75
            lookup["Repeats"].value = 1
            lookup["Size"].value = 250
            statuses = [x for x in all_controls if isinstance(x, widgets.HTML)]
            self.assertTrue(any("Controls changed" in x.value for x in statuses))
            with patch("notebook_ui.run_comparison", side_effect=RuntimeError("UI-test stop before computation")) as runner:
                lookup["Run comparison"].click()
                self.assertFalse(runner.called)  # Prediction is required.
                before = next(x for x in all_controls if isinstance(x, widgets.Textarea) and x.placeholder.startswith("Before"))
                before.value = "TEST: check argument wiring, not a scientific prediction"
                lookup["Run comparison"].click()
                config = runner.call_args.args[0]
                self.assertEqual((config.block_e, config.block_i, config.dt_ms, config.stimulus_pa), (.2,.4,.05,75))
                self.assertEqual((config.n_e, config.n_i), (200,50))
                self.assertEqual(runner.call_args.kwargs["variant"], "external_input")
                self.assertEqual(runner.call_args.kwargs["variant_scale"], 1.2)
                self.assertEqual(runner.call_args.kwargs["seeds"], (11,))
                self.assertFalse(lookup["Run comparison"].disabled)

    def test_evidence_search_widget_updates(self):
        from notebook_ui import evidence_panel
        panel = evidence_panel()
        panel.children[0].value = "Corlett"
        self.assertIn("1 evidence records", panel.children[2].value)
        self.assertIn("stronger subsequent", panel.children[2].value)


if __name__ == "__main__":
    unittest.main()
