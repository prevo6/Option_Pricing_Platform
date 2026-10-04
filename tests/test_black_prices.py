import math
from datetime import datetime
import pytest
from pricing_engine.black import BlackScholes

S, K, R, SIGMA = 31.5, 22.75, 0.05, 0.5
EXPIRY = datetime(2030, 3, 20)


def make(s=S, k=K, r=R, sigma=SIGMA, years=None):

    """Build a BlackScholes; optionally pin T so the result never depends on today's date."""

    bs = BlackScholes(s, k, r, EXPIRY, sigma)
    if years is not None:
        bs.T = years
    return bs



def test_call_matches_textbook_value():
    assert make(100, 100, 0.05, 0.2, years=1.0).call() == pytest.approx(10.4506, abs=1e-3)


def test_put_matches_textbook_value():
    assert make(100, 100, 0.05, 0.2, years=1.0).put() == pytest.approx(5.5735, abs=1e-3)


def test_put_call_parity():
    bs = make()  
    assert bs.call() - bs.put() == pytest.approx(S - K * math.exp(-R * bs.T), abs=1e-9)


def test_call_respects_no_arbitrage_bounds():
    bs = make()
    assert max(S - K * math.exp(-R * bs.T), 0) <= bs.call() <= S


def test_put_respects_no_arbitrage_bounds():
    bs = make()
    assert max(K * math.exp(-R * bs.T) - S, 0) <= bs.put() <= K * math.exp(-R * bs.T)