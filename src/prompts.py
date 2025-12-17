
CONTEXTUALIZATION_OUTPUT_EXAMPLE = '''
{"aligned_sections": [{"section_id_original": "1.1", "section_id_amendment": "1.2", "heading": "Fees", "text_original": "A service fee of 1 USD will be charged", "text_amendment": "service fee is revised to 1.2 USD"}, {"section_id_original": "3.3", "section_id_amendment": "1.3", "heading": "Maintenance", "text_original": "User is liable to pay a maintenance fee of 10 USD per month", "text_amendment": "after careful considerations, maintenance fee has been reduced to 8 USD."}]}
'''

EXTRACTION_OUTPUT_EXAMPLE = '''
{"sections_changed": ["1.1 Fees", "3.3 Maintenance"], "topics_touched": ["Fees", "Maintenance"], "summary_of_the_change": "The Fees section was updated to revise the service fee from 1 USD to 1.2 USD. In the Maintenance section, the maintenance fee has been reduced from 10 USD to 8 USD."}
'''

CONTEXTUALIZATION_PROMPT = (
        "You are Agent 1, a legal document contextualizer.\n"
        "You receive two structured representations of contracts: 'original' and 'amendment'.\n"
        "Your task:\n"
        "1. Normalize their section identifiers where possible.\n"
        "2. You must return a JSON object with a top-level key 'aligned_sections', a list of dictionary with below keys:.\n" \
        "section_id_original, section_id_amendment, heading, text_original, text_amendment.\n"
        "NOTE:"
        "- Your entire response MUST be a single JSON object" \
        "- Do NOT wrap the JSON in markdown code fences (no ```)" \
        "- Do NOT add any text before or after the JSON object"
    )

EXTRACTION_PROMPT = (
        "You are Agent 2, a contract change extractor.\n"
        "You receive an aligned view of sections from original and amendment contracts.\n"
        "Your task:\n"
        "1. Identify exactly which sections changed(section number/name)"
        "2. categorize the topics,\n"
        "3. Generate a detailed summary of all material changes.\n"
        "4. You must return a JSON object with exactly these keys: "
        " sections_changed: List[str], topics_touched: List[str], summary_of_the_change: str.\n"
        "NOTE:"
        "- Your entire response MUST be a single JSON object" \
        "- Do NOT wrap the JSON in markdown code fences (no ```)" \
        "- Do NOT add any text before or after the JSON object"
    )