from reflexos.benchmark import benchmark_tasks, run_benchmark


def test_benchmark_shape_and_policy_savings():
    assert len(benchmark_tasks()) == 40
    report = run_benchmark()
    assert report["baseline_always_astra"]["success_rate"] == 1.0
    assert report["reflexos"]["success_rate"] == 1.0
    assert report["reflexos"]["observed_tokens"] < report["baseline_always_astra"]["observed_tokens"]
    assert report["reflexos"]["cost_units"] < report["baseline_always_astra"]["cost_units"]
    assert report["savings"]["observed_tokens_pct"] > 60
    assert report["savings"]["cost_units_pct"] > 70
    assert report["paths"]["deterministic"] == 16
    assert report["paths"]["luna"] == 14
    assert report["paths"]["luna -> sol"] == 7
    assert report["paths"]["luna -> sol -> astra"] == 3
