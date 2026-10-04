from datetime import datetime
import math

import numpy as np
import pytest

from pricing_engine.monte import MonteCarloSimulation

FAR_FUTURE = datetime(2099, 1, 1)  


def make_mc(S=100, K=100, r=0.05, sigma=0.2, years=1.0, steps=252, sims=20_000):
    """Build a simulation with T and step count pinned so results are date-independent."""
    mc = MonteCarloSimulation(S, K, FAR_FUTURE, r, sigma, sims)
    mc.T = years
    mc.num_of_steps = steps
    mc.dt = years / steps
    return mc


def test_price_before_simulating_returns_sentinel():
    mc = make_mc()
    assert mc._calculate_call_option_price() == -1
    assert mc._calculate_put_option_price() == -1


def test_simulation_is_reproducible():
    a, b = make_mc(sims=1_000), make_mc(sims=1_000)
    a.simulate_prices()
    b.simulate_prices()
    assert np.array_equal(a.simulation_results_S, b.simulation_results_S)


def test_paths_cover_the_full_time_to_expiry():
    """Terminal prices must be evolved for T, not T minus one step."""
    mc = make_mc(steps=10, sims=1_000)
    mc.simulate_prices()
    steps_taken = mc.simulation_results_S.shape[0] - 1
    assert steps_taken * mc.dt == pytest.approx(mc.T)


def test_put_call_parity_on_the_same_paths():
    mc = make_mc(sims=5_000)
    mc.simulate_prices()
    terminal = mc.simulation_results_S[-1]
    expected = math.exp(-mc.r * mc.T) * (terminal.mean() - mc.K)
    assert mc._calculate_call_option_price() - mc._calculate_put_option_price() == pytest.approx(expected, abs=1e-9)