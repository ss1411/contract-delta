# contract-delta
Autonomous Contract Comparison and Change Extraction Agent that can receive two scanned contract images (original and amendment), automatically parse them using vision-capable LLMs, intelligently extract changes through collaborative agents, and return structured, validated outputs that downstream systems can consume.


# Detailed description

This project compares an original contract and its amendment using GPT-4o vision and a two-agent architecture. It parses scanned contract images directly, aligns sections between versions, and outputs a Pydantic-validated JSON payload capturing which sections changed, which business topics are affected, and a detailed summary of the change. The system is designed for integration into legal review queues, compliance workflows, and contract databases, where stable schemas and traceability are critical. GPT-4o handles real-world scan quality issues such as skew, stamps, and low contrast, reducing the need for brittle OCR pre-processing. Langfuse tracing provides deep observability into every step, including model calls, agent reasoning, and validation, making the solution production-ready.


## Demo video:

<iframe src="https://drive.google.com/file/d/1g5MwEY64IfCVYIedzu72ddZbVPfcphXH/preview" width="640" height="480" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe> 


## Architecture and Agent Workflow

The workflow consists of four main stages. First, GPT-4o vision parses each contract image and returns a structured representation of the document hierarchy (title, sections, subsections, and text). Second, Agent 1 (the contextualization agent) consumes both structured representations and normalizes section identifiers while aligning corresponding sections into a common list. Each aligned item contains original and amendment text along with a shared heading. Third, Agent 2 (the extraction agent) focuses only on this aligned structure and identifies which sections changed, which topics those changes impact, and describes the overall effect in a single summary string. Finally, a Pydantic model validates the output and enforces the exact schema expected by downstream systems. Langfuse wraps OpenAI calls and custom spans so that each stage (image parsing, agents, validation) appears as a separate span nested under a single trace.

![Contract Delta workflow](images/contract-delta-workflow.jpg)


## Setup

1. Create and activate a virtual environment.
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Set environment variables(check .env.example):

4. ## Usage
Place test images under `data/test_contracts/` as described below.
```powershell
python -m src.main -o data/test_contracts/pair1_contract1.png -a data/test_contracts/pair1_amendment2.png
```
5. 

Expected output (shape):
```json
{
"sections_changed": ["2.1", "5(b)"],
"topics_touched": ["Pricing", "Termination"],
"summary_of_the_change": "Pricing increased by 20% and a new early termination fee was introduced for cancellations within the first year."
}
```



## Technical Decisions:
Agent collaboration vs. single‑agent (technical decision)
A two‑agent pattern separates concerns: Agent 1 focuses purely on structural alignment of documents, mimicking how a human first builds a mental map of both versions; Agent 2 consumes that map to reason about changes, topics, and summarization. This makes prompts shorter and more focused, which typically improves reliability and reduces prompt‑induced coupling across responsibilities.​

Using GPT‑4o for both multimodal parsing and downstream text‑only reasoning reduces complexity: a single provider, consistent tokenization, and integrated Langfuse tracing across all calls. GPT‑4o is optimized for image+text tasks and can handle noisy scanned documents more robustly than classical OCR plus text‑only models, which is important for real‑world legal scans with stamps, handwriting, or skewed pages.


## Why Two Agents and Why GPT-4o?

A single prompt that both aligns sections and reasons about changes tends to become long, brittle, and harder to maintain. Splitting responsibilities into two agents keeps prompts focused and makes failures easier to debug: if alignment is wrong, only Agent 1 needs adjustment; if topics are misclassified, Agent 2 can be tuned independently. This mirrors how legal analysts work: they first map the structure of documents and only then reason about differences. GPT-4o is used for both the multimodal parsing and agent reasoning because it natively handles images and text, reducing the integration surface area. Its image understanding capabilities are more robust on scanned documents than legacy OCR pipelines, and using a single model family simplifies prompt design and observability through Langfuse’s OpenAI integration.

## Langfuse Tracing Guide

After setting LANGFUSE environment variables and running the CLI command, navigate to your Langfuse dashboard. Under Traces, you will see entries named `contract_change_workflow`, each representing a full run comparing two contracts. Expanding a trace shows child spans such as `image_parsing`, `contextualization`, `extraction`, and `pydantic_validation`, and each OpenAI call is automatically nested inside the appropriate span. This view lets you inspect prompts, model responses, token usage, and latencies, which is essential for optimizing cost and debugging misclassifications in production.

![langfuse example run screenshot](images/example-run-langfuse.png)

-------------------------------------------------------------------------------------------------------------------
| Aspect             | Choice                        | Rationale                                                   |
| ------------------ | ----------------------------- | ------------------------------------------------------------|
| Vision model       | GPT‑4o                        | Native image+text support, robust on scans, single provider.|
| Agent pattern      | Two agents (A1 + A2)          | Separation of concerns, easier debugging and prompt tuning. |
| Schema enforcement | Pydantic ContractChange       | Strong typing, safe integrations, clear error handling.​     |
| Observability      | Langfuse + OpenAI integration | Automatic tracing of all OpenAI calls and spans.​            |
| CLI entrypoint     | src/main.py via argparse      | Simple automation and CI integration.                       |
--------------------------------------------------------------------------------------------------------------------


## Example Runs:

----------- Run 1-----------
Issue faced: was getting the json object wrapped inside triple backticks due to which it was not getting correctly parsed.

```powershell
(.venv_contractdelta) PS C:\work\projects\contract-delta> python -m src.main -o data/test_contracts/pair1_contract1.png -a data/test_contracts/pair1_amendment2.png
=== Extraction agent raw output ===
 ```json
{
  "sections_changed": [
    "1",
    "2",
    "3"
  ],
  "topics_touched": [
    "Services",
    "Compensation",
    "Term and Termination"
  ],
  "summary_of_the_change": "The amendment modifies the Services section to indicate that the Services Agreement is updated. The Compensation section is revised to specify a monthly fee of $6,000.00. The Term and Termination section introduces an early termination fee of $10,000 if the Client terminates within the first year."
}
```
{
  "sections_changed": [],
  "topics_touched": [],
  "summary_of_the_change": "Could not parse Agent 2 JSON; raw response: ```json\n{\n  \"sections_changed\": [\n    \"1\",\n    \"2\",\n    \"3\"\n  ],\n  \"topics_touched\": [\n    \"Services\",\n    \"Compensation\",\n    \"Term and Termination\"\n  ],\n  \"summary_of_the_change\": \"The amendment modifies the Services section to indicate that the Services Agreement is updated. The Compensation section is revised to specify a monthly fee of $6,000.00. The Term and Termination section introduces an early termination fee of $10,000 if the Client terminates within the first year.\"\n}\n```"
}
```

------- Run 2 ------------
Resolved the markdown/triple backticks issue by:
- adding additional instructions in prompt to handle backticks
- used regex to remove any such markdown before passing the output to json.loads()

```powershell
(.venv_contractdelta) PS C:\work\projects\contract-delta> python -m src.main -o data/test_contracts/pair1_contract1.png -a data/test_contracts/pair1_amendment2.png

=== Extraction agent cleaned output ===
 {
  "sections_changed": [
    "2",
    "3",
    "5"
  ],
  "topics_touched": [
    "Pricing",
    "Termination",
    "General Provisions"
  ],
  "summary_of_the_change": "The original pricing section of the contract was updated to reflect a new fee of $6,000.00 per month, replacing the previous fee of $5,000.00. Additionally, a new clause regarding an early termination fee of $10,000 was introduced if the Client terminates the agreement within the first year. Lastly, the general provisions section remains unchanged in content but is associated with the newly added termination fee clause."
}
```

--------- Run 3 with 2nd pair of inputs ------------------
```powershell
(.venv_contractdelta) PS C:\work\projects\contract-delta> python -m src.main -o data/test_contracts/contract2.png -a data/test_contracts/contract2-amendment.png
Parsing contract images with vision model...
Running contextualization agent...
Running extraction agent...
Running pydantic validation of final output...
{
  "sections_changed": [
    "49",
    "51",
    "52",
    "53"
  ],
  "topics_touched": [
    "Entire Agreement",
    "Obligations of Allottee",
    "Severability",
    "Payment Provisions"
  ],
  "summary_of_the_change": "In Section 49 (Entire Agreement), the amendment specifies that both verbal and written commitments by the Promoter are recognized. In Section 51 (Obligations of Allottee), it is added that the original Allottee remains liable for any dues or breaches before the transfer date. Section 52 (Severability) is expanded to explicitly state that remaining provisions stay enforceable after amendments. Section 53 (Payment Provisions) introduces a fee for late payments and specifies that calculation of proportionate shares will include any additional amenities provided."
}
```

## Running Tests:

From project root (folder that contains src/ and tests/), 
```
# PowerShell
$env:PYTHONPATH = "."
pytest tests/test_pydantic_validation.py

# cmd.exe
set PYTHONPATH=.
pytest tests\test_pydantic_validation.py
```

Now run tests with pytest:
1. Run all tests within one file:
```
pytest tests/test_pydantic_validation.py
```

2. Run a specific test function from a file:
```
pytest tests/test_pydantic_validation.py::test_valid_payload_passes
```
you can add -v option for verbose output

3. Run all tests in tests/ folder
```
pytest
# or explicitly:
pytest tests
```

## Example test runs:

```powershell
(.venv_contractdelta) PS C:\work\projects\contract-delta> $env:PYTHONPATH = "."
(.venv_contractdelta) PS C:\work\projects\contract-delta> pytest tests/test_pydantic_validation.py
========================================================================= test session starts ==========================================================================
platform win32 -- Python 3.13.1, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\work\projects\contract-delta
plugins: anyio-4.12.0
collected 2 items                                                                                                                                                       

tests\test_pydantic_validation.py ..                                                                                                                              [100%]

========================================================================== 2 passed in 0.46s ===========================================================================
(.venv_contractdelta) PS C:\work\projects\contract-delta> pytest tests/test_image_parsing.py      
========================================================================= test session starts ==========================================================================
platform win32 -- Python 3.13.1, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\work\projects\contract-delta
plugins: anyio-4.12.0
collected 2 items                                                                                                                                                       

tests\test_image_parsing.py ..                                                                                                                                    [100%]

========================================================================== 2 passed in 5.14s ===========================================================================
(.venv_contractdelta) PS C:\work\projects\contract-delta> pytest tests/test_agent_handoff.py      
========================================================================= test session starts ==========================================================================
platform win32 -- Python 3.13.1, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\work\projects\contract-delta
plugins: anyio-4.12.0
collected 1 item                                                                                                                                                        

tests\test_agent_handoff.py .                                                                                                                                     [100%]

========================================================================== 1 passed in 9.56s =========================================================================== 
(.venv_contractdelta) PS C:\work\projects\contract-delta> 
```
