from datetime import datetime
import math

import pytest

from pricing_engine.binomial import BinomialTree, BinomialTreeVisual

FAR_FUTURE = datetime(2099, 1, 1) 


def make_tree(S=100, K=100, r=0.05, sigma=0.2, years=1.0, N=500):
    """Build a tree with T pinned so results never depend on today's date."""
    tree = BinomialTree(S, K, FAR_FUTURE, r, sigma, N)
    tree.T = years
    return tree


def test_one_step_tree_matches_hand_calculation():
    S, K, r, sigma, T = 100, 100, 0.05, 0.2, 1.0
    u = math.exp(sigma * math.sqrt(T))
    d = 1 / u
    p = (math.exp(r * T) - d) / (u - d)
    expected = math.exp(-r * T) * (p * max(S * u - K, 0) + (1 - p) * max(S * d - K, 0))
    assert make_tree(N=1).calculate_call() == pytest.approx(expected)


def test_put_call_parity_holds_exactly():
    tree = make_tree(N=200)
    assert tree.calculate_call() - tree.calculate_put() == pytest.approx(100 - 100 * math.exp(-0.05), abs=1e-6)


def test_deep_in_the_money_call_is_about_intrinsic_value():
    tree = make_tree(S=200, K=100)
    assert tree.calculate_call() == pytest.approx(200 - 100 * math.exp(-0.05), abs=0.05)


def test_prices_move_the_right_way():
    assert make_tree(sigma=0.4).calculate_call() > make_tree(sigma=0.2).calculate_call()
    assert make_tree(S=110).calculate_call() > make_tree(S=100).calculate_call()
    assert make_tree(S=110).calculate_put() < make_tree(S=100).calculate_put()


class TestVisualTree:
    def test_root_value_matches_the_pricer(self):
        tree = make_tree(N=5)
        visual = BinomialTreeVisual(tree)
        assert visual.build_tree() == pytest.approx(tree.calculate_call())

    def test_tree_recombines(self):
        visual = BinomialTreeVisual(make_tree(N=5))
        visual.build_tree()
        assert visual.stock_tree[0, 0] == pytest.approx(100)
        assert visual.stock_tree[2, 1] == pytest.approx(100)  # one up + one down returns to start
        assert visual.stock_tree[4, 2] == pytest.approx(100)

    def test_terminal_values_are_call_payoffs(self):
        visual = BinomialTreeVisual(make_tree(N=5))
        visual.build_tree()
        for j in range(6):
            assert visual.value_tree[5, j] == pytest.approx(max(visual.stock_tree[5, j] - 100, 0))

    def test_unused_upper_triangle_stays_zero(self):
        visual = BinomialTreeVisual(make_tree(N=5))
        visual.build_tree()
        assert visual.stock_tree[1, 2] == 0