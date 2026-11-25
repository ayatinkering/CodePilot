from codepilot.runner import classify, run_tests


def test_no_docker_fallback(tmp_path):
    assert run_tests(tmp_path, "") == {
        "status": "environment_error",
        "reason": "runner_image_digest_required",
    }


def test_result_classification():
    assert classify(None, 0) == "environment_error"
    assert classify({"tests": []}, 0) == "zero_tests"
    assert classify({"tests": [{"outcome": "failed"}]}, 1) == "baseline_failed"
    assert classify({"tests": [{"outcome": "passed"}]}, 0) == "passed"
    assert (
        classify({"tests": [{"outcome": "passed"}], "collection_errors": ["import"]}, 2)
        == "environment_error"
    )
    assert classify({"tests": [{"outcome": "skipped"}]}, 0) == "zero_tests"
