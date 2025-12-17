from src.agents.extraction_agent import run_extraction_agent


def test_agent_handoff_shape():
    # Minimal aligned structure stub simulating Agent 1 output.
    context_stub = {
        "aligned_sections": [
            {
                "section_id_original": "2.1",
                "section_id_amendment": "2.1",
                "heading": "Fees",
                "text_original": "Fee is 100 USD per month.",
                "text_amendment": "Fee is 120 USD per month.",
            }
        ]
    }

    result = run_extraction_agent(context_stub)
    assert "sections_changed" in result
    assert "topics_touched" in result
    assert "summary_of_the_change" in result
