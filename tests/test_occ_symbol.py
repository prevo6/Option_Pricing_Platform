import pandas as pd
import pytest

from etl_scripts.alpaca.transform import _parse_occ_symbol


def test_parses_a_call():
    result = _parse_occ_symbol("SPX260821C00200000")
    assert result["underlying"] == "SPX"
    assert result["side"] == "call"
    assert result["strike"] == 200.0
    assert result["expiration"] == pd.Timestamp("2026-08-21")


def test_parses_a_put():
    result = _parse_occ_symbol("AAPL251219P00150000")
    assert result["underlying"] == "AAPL"
    assert result["side"] == "put"
    assert result["strike"] == 150.0
    assert result["expiration"] == pd.Timestamp("2025-12-19")


def test_strike_is_encoded_in_thousandths():
    assert _parse_occ_symbol("SPY260821C00432500")["strike"] == 432.5
    assert _parse_occ_symbol("SPY260821C00000500")["strike"] == 0.5
    assert _parse_occ_symbol("SPX260821C07600000")["strike"] == 7600.0


@pytest.mark.parametrize("bad", ["", "SPX", "spx260821c00200000", "SPX260821X00200000", "SPX26082C00200000", "SPX260821C0020000"])
def test_malformed_symbols_raise_a_clear_error(bad):
    with pytest.raises(ValueError):
        _parse_occ_symbol(bad)