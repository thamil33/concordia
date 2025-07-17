def parse_llm_list_response(response: str, separator: str = '***', min_items: int = 2) -> list[str]:
    """
    Parse a list-like response from an LLM, splitting by a separator and validating item count.

    Args:
        response: The raw string response from the LLM.
        separator: The string used to separate items in the response.
        min_items: Minimum number of items required for the response to be considered valid.

    Returns:
        A list of stripped items.

    Raises:
        ValueError: If the number of items is less than min_items.
    """
    items = [item.strip() for item in response.split(separator) if item.strip()]
    if len(items) < min_items:
        raise ValueError(f"Expected at least {min_items} items, got: {items}")
    return items


def validate_llm_output_format(response: str, required_substrings: list[str] = None) -> bool:
    """
    Validate that the LLM response contains all required substrings.

    Args:
        response: The raw string response from the LLM.
        required_substrings: List of substrings that must be present in the response.

    Returns:
        True if all required substrings are present, False otherwise.
    """
    if not required_substrings:
        return True
    return all(sub in response for sub in required_substrings)
