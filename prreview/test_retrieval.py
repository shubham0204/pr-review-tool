from prreview.retrieval import get_pr_details, run_pylint_on_string


def test_get_pr_details():
    pr = get_pr_details("shubham0204", "SmolChat-Android", 56)
    assert pr.number == 56
    assert pr.title == "Add Llama server (OpenAI compatible)"
    assert len(pr.changed_files_urls) == 18


def test_run_pylint_on_string():
    response = run_pylint_on_string(
        """
        import math
        print("Hello World")                              
        """
    )
    assert len(response) > 0
