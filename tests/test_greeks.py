"""
Greek tests using finite differences: reprice with a slightly bumped input and
compare against the analytic greek. No hardcoded reference values, so these
never go stale as datetime.now() moves.

Assumes BlackScholes(S, K, r, T, sigma, isCall=True) with .call()/.put()
price methods. Adjust the `price` helper if your class exposes pricing differently.
"""

from datetime import datetime, timedelta

import pytest

from pricing_engine.black import BlackScholes

S, K, R, SIGMA = 31.5, 22.5, 0.05, 0.5
EXPIRY = datetime(2030, 3, 20)


def price(is_call: bool, *, s=S, k=K, r=R, expiry=EXPIRY, sigma=SIGMA) -> float:
    bs = BlackScholes(s, k, r, expiry, sigma, isCall=is_call)
    return bs.call() if is_call else bs.put()


@pytest.mark.parametrize("is_call", [True, False])
def test_theta_matches_one_day_of_decay(is_call):
    theta = BlackScholes(S, K, R, EXPIRY, SIGMA, isCall=is_call).theta()
    one_day_later = price(is_call, expiry=EXPIRY - timedelta(days=1)) - price(is_call)
    assert theta == pytest.approx(one_day_later, abs=1e-4)


@pytest.mark.parametrize("is_call", [True, False])
def test_vega_matches_one_vol_point(is_call):
    vega = BlackScholes(S, K, R, EXPIRY, SIGMA, isCall=is_call).vega()
    bump = (price(is_call, sigma=SIGMA + 0.01) - price(is_call, sigma=SIGMA - 0.01)) / 2
    assert vega == pytest.approx(bump, abs=1e-3)


@pytest.mark.parametrize("is_call", [True, False])
def test_rho_matches_one_rate_point(is_call):
    rho = BlackScholes(S, K, R, EXPIRY, SIGMA, isCall=is_call).rho()
    bump = (price(is_call, r=R + 0.01) - price(is_call, r=R - 0.01)) / 2
    assert rho == pytest.approx(bump, abs=1e-3)


def test_vega_is_the_same_for_calls_and_puts():
    call = BlackScholes(S, K, R, EXPIRY, SIGMA, isCall=True).vega()
    put = BlackScholes(S, K, R, EXPIRY, SIGMA, isCall=False).vega()
    assert call == pytest.approx(put)