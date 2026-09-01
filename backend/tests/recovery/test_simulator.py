from app.recovery.simulator import simulate_execution

def test_simulator_deterministic():
    # Same input -> same output
    res1 = simulate_execution("RETRY", 1000, 0.8, "NETWORK_ERROR", 1, "card")
    res2 = simulate_execution("RETRY", 1000, 0.8, "NETWORK_ERROR", 1, "card")
    
    assert res1 == res2
    
def test_simulator_different_input():
    res1 = simulate_execution("RETRY", 1000, 0.8, "NETWORK_ERROR", 1, "card")
    res2 = simulate_execution("RETRY", 1000, 0.2, "INSUFFICIENT_FUNDS", 4, "upi")
    
    assert res1 != res2
    
def test_no_action():
    res = simulate_execution("NO_ACTION", 1000, 0.5, "UNKNOWN", 1, "card")
    assert res["success"] is False
    assert res["recovered_amount"] == 0
    
def test_payment_link():
    res = simulate_execution("PAYMENT_LINK", 1000, 0.5, "UNKNOWN", 1, "card")
    assert res["success"] is True
    assert res["recovered_amount"] == 0 # Doesn't immediately recover
    
def test_money_is_integer():
    res = simulate_execution("RETRY", 1500, 1.0, "NETWORK_ERROR", 1, "card")
    # if it succeeds, recovered_amount should be int
    assert isinstance(res["recovered_amount"], int)
