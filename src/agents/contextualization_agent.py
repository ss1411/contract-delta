"""
Agent 1: analyzes both documents, identifies structure and corresponding sections.
"""

from typing import Any, Dict
from langfuse.openai import OpenAI
from src.prompts import CONTEXTUALIZATION_PROMPT
from src.utils import extract_json_from_markdown

client = OpenAI()


def build_contextualization_system_prompt() -> str:
    """
    Agent 1's instructions: build aligned structure for both documents.
    """
    return CONTEXTUALIZATION_PROMPT


def run_contextualization_agent(
    original_doc: Dict[str, Any],
    amendment_doc: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Agent 1: takes parsed contract outputs and aligns sections between original and amendment.
    """
    system_prompt = build_contextualization_system_prompt()

    # Agent leverage: single multimodal call with text-only inputs (structured JSON from vision)
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
                            "Here is the original contract JSON:\n"
                            f"{original_doc['raw_text']}\n\n"
                            "Here is the amendment contract JSON:\n"
                            f"{amendment_doc['raw_text']}\n\n"
                            "Produce the aligned JSON as specified."
                        ),
                    }
                ],
            },
        ],
        max_output_tokens=800,
    )

    content = response.output[0].content[0].text
    clean_content = extract_json_from_markdown(content)
    # print("=== Contextualization agent raw output ===\n", clean_content)

    # Expect JSON; parse with json.loads plus defensive handling in real code.
    import json

    try:
        return json.loads(clean_content)
    except json.JSONDecodeError:
        # Fallback: wrap raw text so downstream code can still inspect.
        return {"aligned_sections_raw": content}
