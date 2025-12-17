"""
Agent 2: receives Agent 1's output, extracts specific changes. Shows clear handoff mechanism
"""

from typing import Any, Dict
from langfuse.openai import OpenAI
from src.models import validate_change_payload  # Pydantic validation + error handling
from src.prompts import EXTRACTION_PROMPT
from src.utils import extract_json_from_markdown

client = OpenAI()


def build_extraction_system_prompt() -> str:
    """
    Agent 2's instructions: produce final ContractChange payload.
    """
    return EXTRACTION_PROMPT


def run_extraction_agent(context_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Agent 2: takes Agent 1's aligned sections and outputs a ContractChange dict.
    """
    system_prompt = build_extraction_system_prompt()

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Here is the aligned section structure from Agent 1:\n"
                            f"{context_output}\n\n"
                            "Identify changes and respond with the required JSON."
                        ),
                    }
                ],
            },
        ],
        max_output_tokens=800,
    )

    raw_text = response.output[0].content[0].text
    clean_text = extract_json_from_markdown(raw_text)
    # print("=== Extraction agent cleaned output ===\n", clean_text)

    import json

    try:
        raw_dict = json.loads(clean_text)
    except json.JSONDecodeError:
        # Wrap in a minimal structure to make validation failures explicit.
        raw_dict = {
            "sections_changed": [],
            "topics_touched": [],
            "summary_of_the_change": f"Could not parse Agent 2 JSON; raw response: {raw_text}",
        }

    # Final guardrail: ensure shape is correct for downstream systems.
    validated = validate_change_payload(raw_dict)
    return validated.model_dump()
