"""
Defines Pydantic model with exactly these three fields:
- sections_changed: List[str] with specific section identifiers
- topics_touched: List[str] with business/legal topic categories
- summary_of_the_change: str with detailed change description

Output passes Pydantic validation (.model_validate() or equivalent succeeds)
"""

from typing import List
from pydantic import BaseModel, Field, ValidationError


class ContractChange(BaseModel):
    """
    Stable schema for downstream systems: legal DBs, review queues, dashboards.
    """
    sections_changed: List[str] = Field(
        description="List of section identifiers that changed, eg. ['2.1', '5(b)']"
    )
    topics_touched: List[str] = Field(
        description="High-level legal topics (e.g., 'Termination', 'Liability')"
    )
    summary_of_the_change: str = Field(
        description="Detailed natural-language summary capturing what changed between the two contract versions."
    )


def validate_change_payload(raw: dict) -> ContractChange:
    """
    Wraps Pydantic validation with graceful error reporting.
    """
    try:
        return ContractChange(**raw)
    except ValidationError as e:
        # In production this would be logged and traced; here we raise a clean error.
        # Pydantic exposes .errors(), .error_count(), and .json() for structured inspection.
        raise ValueError(
            f"Invalid ContractChange payload: {e.errors()}"
        ) from e
