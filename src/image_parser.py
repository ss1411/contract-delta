"""
Includes Functions for: 
- image validation (format, size), 
- encoding (base64 or URL), 
- multimodal API calls with proper message formatting, 
- vision-specific prompts for contract parsing.
"""

import base64
from pathlib import Path
from typing import List, Dict, Any

from langfuse.openai import OpenAI  # wrapped OpenAI client for automatic tracing

client = OpenAI()  # uses OPENAI_API_KEY from env


SUPPORTED_EXTS = {".png", ".jpg", ".jpeg"}


def validate_image_path(path_str: str) -> Path:
    """
    Validates file existence, extension, and non-zero size.
    
    Args:
        path_str: File path as string.
    
    Returns:
        Path: Validated Path object.
    
    Raises:
        FileNotFoundError: If file does not exist.
        ValueError: If format unsupported or file is empty.
    """
    p = Path(path_str)
    if not p.exists():
        raise FileNotFoundError(f"Image not found: {p}")
    if p.suffix.lower() not in SUPPORTED_EXTS:
        raise ValueError(f"Unsupported image format {p.suffix}, expected one of {SUPPORTED_EXTS}")
    if p.stat().st_size == 0:
        raise ValueError(f"Image is empty: {p}")
    return p


def encode_image_to_base64(path: Path) -> str:
    """
    Returns base64-encoded image string suitable for OpenAI vision calls.
    
    Args:
        path: Validated Path object to image file.
    
    Returns:
        str: Base64-encoded image string.
    """
    with path.open("rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def build_contract_vision_prompt() -> str:
    """
    Vision-specific prompt to instruct GPT-4o to output structured hierarchy for contracts. [web:12]
    """
    return (
        "You are a contract parsing engine. Extract a strictly structured JSON representing "
        "the document hierarchy. Identify sections, subsections, headings, and their text. "
        "Example top-level keys: 'title', 'parties', 'sections'. "
        "Each section should include an 'id' (e.g., '2.1' or 'Section 5(b)'), 'heading', "
        "and 'body'. Do not include comments, only relevant/required structured content."
    )


def parse_contract_images_with_vision(image_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Calls GPT-4o in multimodal mode to parse each contract image into a structured JSON.
    Uses base64-encoded images for local files.
    
    Args:
        image_paths: List of file paths to contract images.
    
    Returns:
        List[Dict[str, Any]]: List of parsed documents, each containing raw extracted text.
    """
    prompt = build_contract_vision_prompt()
    parsed_docs: List[Dict[str, Any]] = []

    for path_str in image_paths:
        path = validate_image_path(path_str)
        b64 = encode_image_to_base64(path)

        # Using Responses API for multimodal: text + image
        response = client.responses.create(
            model="gpt-4o",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": f"data:image/{path.suffix.lstrip('.').lower()};base64,{b64}"},
                    ],
                }
            ],
            max_output_tokens=4000,
        )

        text_out = response.output[0].content[0].text
        parsed_docs.append({"raw_text": text_out})

    return parsed_docs
