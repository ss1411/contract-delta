"""
Entry point that: 
(1) accepts two image file paths as arguments
(2) calls multimodal LLM to parse both images
(3) executes Agent 1 (contextualization)
(4) executes Agent 2 (change extraction)
(5) validates output with Pydantic
(6) returns structured JSON. Must be runnable from command line.
"""

import os
import argparse
import json
from typing import List

from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path, override=True)

from langfuse import get_client, propagate_attributes

from src.image_parser import parse_contract_images_with_vision
from src.agents.contextualization_agent import run_contextualization_agent
from src.agents.extraction_agent import run_extraction_agent
from src.models import validate_change_payload
from src.utils import setup_logger

# setup logger
logger = setup_logger(__name__)

# Initialize Langfuse client to capture custom traces
lf = get_client()


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Compare two contract images (original + amendment) using GPT-4o vision and a two-agent system."
    )
    parser.add_argument("--original_image", "-o", type=str, help="Path to original contract image file")
    parser.add_argument("--amendment_image", "-a", type=str, help="Path to amendment contract image file")
    args = parser.parse_args(argv)
    # Top-level trace
    with lf.start_as_current_observation(as_type="span", name="contract_change_workflow", input={"contract": args.original_image, "amendment": args.amendment_image}) as root_span:
        with propagate_attributes(session_id="test-session", user_id="test-user"):
            
            # 1) Image parsing (multimodal)
            logger.info("Parsing contract images with vision model...")
            with lf.start_as_current_observation(as_type="span", name="image_parsing") as span:
                parsed_docs = parse_contract_images_with_vision(
                    [args.original_image, args.amendment_image]
                )
                original_doc, amendment_doc = parsed_docs
                span.update(output={"original_doc": original_doc, "amendment_doc": amendment_doc})
            root_span.update_trace(metadata={"original_length": len(original_doc['raw_text']), "amendment_length": len(amendment_doc['raw_text'])})
            
            # 2) Agent 1: contextualization
            logger.info("Running contextualization agent...")
            with lf.start_as_current_observation(as_type="span", name="contextualization") as span:
                context_output = run_contextualization_agent(original_doc, amendment_doc)
                span.update(output=context_output)
            root_span.update_trace(metadata={"aligned_sections": len(context_output.get("aligned_sections", []))})
            
            # 3) Agent 2: extraction
            logger.info("Running extraction agent...")
            with lf.start_as_current_observation(as_type="span", name="extraction") as span:
                extraction_raw = run_extraction_agent(context_output)
                span.update(output=extraction_raw)
            root_span.update_trace(metadata={"sections_changed": len(extraction_raw.get("sections_changed", []))}) 

            # 4) Final Pydantic validation
            logger.info("Running pydantic validation of final output...")
            with lf.start_as_current_observation(as_type="span", name="pydantic_validation") as span:
                validated = validate_change_payload(extraction_raw)
                span.update(output=validated.model_dump())
            root_span.update_trace(metadata={"validation_success": True})
            root_span.update(input={"original_doc": original_doc, "amendment_doc": amendment_doc, "context_output": context_output, "extraction_raw": extraction_raw}, output=validated.model_dump())
            # 5) output JSON to stdout for CLI usage
            print(json.dumps(validated.model_dump(), indent=2))


if __name__ == "__main__":
    main()
