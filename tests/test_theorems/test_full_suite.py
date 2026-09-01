from hijaiyyah.theorems.test_suite import TheoremTestSuite


def test_all_13_pass():
    results = TheoremTestSuite().run_all()
    for r in results:
        assert r.passed, f"{r.ref}: {r.message}"
